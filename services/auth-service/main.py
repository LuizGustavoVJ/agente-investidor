"""
Serviço de Autenticação - Agente Investidor
Responsável por autenticação, autorização e gerenciamento de usuários
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import structlog
import time
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import redis
import json

# Configuração de logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Métricas Prometheus
REQUEST_COUNT = Counter('auth_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('auth_request_duration_seconds', 'Request duration')
LOGIN_ATTEMPTS = Counter('auth_login_attempts_total', 'Login attempts', ['status'])
TOKEN_VALIDATIONS = Counter('auth_token_validations_total', 'Token validations', ['status'])

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Auth Service",
    description="Serviço de Autenticação e Autorização",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except jwt.PyJWTError:
        return None

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(duration)
    
    return response

# Health check
@app.get("/health")
async def health_check():
    try:
        # Verificar Redis
        redis_client.ping()
        return {
            "status": "healthy",
            "service": "auth-service",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "redis": "healthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Métricas endpoint
@app.get("/metrics")
async def metrics():
    return generate_latest()

# Simulated user database (em produção, usar PostgreSQL)
fake_users_db = {}

# Auth endpoints
@app.post("/register", response_model=dict)
async def register(user: UserCreate):
    start_time = time.time()
    
    try:
        # Verificar se usuário já existe
        if user.email in fake_users_db:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Hash da senha
        hashed_password = get_password_hash(user.password)
        
        # Criar usuário
        user_id = f"user_{len(fake_users_db) + 1}"
        fake_users_db[user.email] = {
            "id": user_id,
            "email": user.email,
            "hashed_password": hashed_password,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        logger.info("User registered", email=user.email, user_id=user_id)
        
        return {
            "message": "User registered successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    try:
        # Verificar usuário
        user = fake_users_db.get(user_credentials.email)
        if not user or not verify_password(user_credentials.password, user["hashed_password"]):
            LOGIN_ATTEMPTS.labels(status="failed").inc()
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        # Criar tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user["email"]})
        
        # Salvar refresh token no Redis
        redis_client.setex(
            f"refresh_token:{user['id']}", 
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), 
            refresh_token
        )
        
        LOGIN_ATTEMPTS.labels(status="success").inc()
        logger.info("User logged in", email=user["email"], user_id=user["id"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    try:
        # Verificar refresh token
        token_data = verify_token(refresh_token)
        if token_data is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = fake_users_db.get(token_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Verificar se refresh token existe no Redis
        stored_token = redis_client.get(f"refresh_token:{user['id']}")
        if not stored_token or stored_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Criar novos tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": user["email"]})
        
        # Atualizar refresh token no Redis
        redis_client.setex(
            f"refresh_token:{user['id']}", 
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), 
            new_refresh_token
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post("/validate")
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            TOKEN_VALIDATIONS.labels(status="invalid").inc()
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = fake_users_db.get(token_data.email)
        if not user:
            TOKEN_VALIDATIONS.labels(status="user_not_found").inc()
            raise HTTPException(status_code=401, detail="User not found")
        
        TOKEN_VALIDATIONS.labels(status="valid").inc()
        
        return {
            "valid": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token validation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Token validation failed")

@app.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = fake_users_db.get(token_data.email)
        if user:
            # Remover refresh token do Redis
            redis_client.delete(f"refresh_token:{user['id']}")
            logger.info("User logged out", email=user["email"], user_id=user["id"])
        
        return {"message": "Logged out successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(status_code=500, detail="Logout failed")

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_config=None  # Usar structlog
    )

