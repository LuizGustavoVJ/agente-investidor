"""
Serviço de Autenticação - Agente Investidor
Responsável por autenticação, autorização e gerenciamento de usuários
Integrado com frontend Vue.js
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Response, Request
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

# Frontend URLs para CORS
FRONTEND_URLS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "https://agente-investidor-frontend.vercel.app",
    "https://agenteinvestidor.com"
]

# Redis connection with retry logic
def get_redis_client():
    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        client.ping()
        return client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        return None

redis_client = get_redis_client()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Auth Service",
    description="Serviço de Autenticação e Autorização integrado com Frontend Vue.js",
    version="2.0.0"
)

# CORS configurado para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

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

def create_refresh_token(data: dict, remember_me: bool = False):
    to_encode = data.copy()
    days = REFRESH_TOKEN_EXPIRE_DAYS * 4 if remember_me else REFRESH_TOKEN_EXPIRE_DAYS
    expire = datetime.utcnow() + timedelta(days=days)
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

def set_secure_cookie(response: Response, name: str, value: str, max_age: int):
    """Define cookie seguro HTTP-only"""
    response.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production",
        samesite="lax"
    )

def get_cookie_from_request(request: Request, name: str) -> Optional[str]:
    """Obtém cookie da requisição"""
    return request.cookies.get(name)

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
        # Verificar Redis se disponível
        redis_status = "healthy"
        if redis_client:
            redis_client.ping()
        else:
            redis_status = "unavailable"
            
        return {
            "status": "healthy",
            "service": "auth-service",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "redis": redis_status
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Métricas endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Simulated user database (em produção, usar PostgreSQL)
fake_users_db = {
    "admin@agenteinvestidor.com": {
        "id": "user_1",
        "email": "admin@agenteinvestidor.com",
        "hashed_password": pwd_context.hash("admin123"),
        "name": "Administrador",
        "is_active": True,
        "created_at": datetime.utcnow()
    },
    "demo@agenteinvestidor.com": {
        "id": "user_2", 
        "email": "demo@agenteinvestidor.com",
        "hashed_password": pwd_context.hash("demo123"),
        "name": "Usuário Demo",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
}

# Auth endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserCreate, response: Response):
    try:
        # Verificar se usuário já existe
        if user.email in fake_users_db:
            raise HTTPException(
                status_code=409,
                detail="Email já está em uso"
            )
        
        # Hash da senha
        hashed_password = get_password_hash(user.password)
        
        # Criar usuário
        user_id = f"user_{len(fake_users_db) + 1}"
        user_data = {
            "id": user_id,
            "email": user.email,
            "hashed_password": hashed_password,
            "name": user.name,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        fake_users_db[user.email] = user_data
        
        # Criar tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        # Definir cookies seguros
        set_secure_cookie(response, "access_token", access_token, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        set_secure_cookie(response, "refresh_token", refresh_token, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
        
        # Salvar refresh token no Redis se disponível
        if redis_client:
            redis_client.setex(
                f"refresh_token:{user_id}", 
                timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), 
                refresh_token
            )
        
        logger.info("User registered", email=user.email, user_id=user_id)
        
        return TokenResponse(
            user=UserResponse(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                is_active=user_data["is_active"],
                created_at=user_data["created_at"]
            ),
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, response: Response):
    try:
        # Verificar usuário
        user = fake_users_db.get(user_credentials.email)
        if not user or not verify_password(user_credentials.password, user["hashed_password"]):
            LOGIN_ATTEMPTS.labels(status="failed").inc()
            raise HTTPException(
                status_code=401,
                detail="Credenciais inválidas"
            )
        
        # Criar tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user["email"]}, 
            remember_me=user_credentials.remember_me
        )
        
        # Definir cookies seguros
        max_age_refresh = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        if user_credentials.remember_me:
            max_age_refresh *= 4
            
        set_secure_cookie(response, "access_token", access_token, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        set_secure_cookie(response, "refresh_token", refresh_token, max_age_refresh)
        
        # Salvar refresh token no Redis se disponível
        if redis_client:
            redis_client.setex(
                f"refresh_token:{user['id']}", 
                timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS * (4 if user_credentials.remember_me else 1)), 
                refresh_token
            )
        
        LOGIN_ATTEMPTS.labels(status="success").inc()
        logger.info("User logged in", email=user["email"], user_id=user["id"])
        
        return TokenResponse(
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                is_active=user["is_active"],
                created_at=user["created_at"]
            ),
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/auth/refresh", response_model=dict)
async def refresh_token_endpoint(request: Request, response: Response):
    try:
        # Obter refresh token do cookie
        refresh_token = get_cookie_from_request(request, "refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token não encontrado")
        
        # Verificar refresh token
        token_data = verify_token(refresh_token)
        if token_data is None:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        
        user = fake_users_db.get(token_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        # Verificar se refresh token existe no Redis (se disponível)
        if redis_client:
            stored_token = redis_client.get(f"refresh_token:{user['id']}")
            if not stored_token or stored_token != refresh_token:
                raise HTTPException(status_code=401, detail="Refresh token inválido")
        
        # Criar novos tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": user["email"]})
        
        # Atualizar cookies
        set_secure_cookie(response, "access_token", new_access_token, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        set_secure_cookie(response, "refresh_token", new_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
        
        # Atualizar refresh token no Redis se disponível
        if redis_client:
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
        raise HTTPException(status_code=500, detail="Erro ao renovar token")

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(request: Request):
    try:
        # Obter token do cookie ou header
        access_token = get_cookie_from_request(request, "access_token")
        if not access_token:
            # Tentar obter do header Authorization
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Token não fornecido")
        
        token_data = verify_token(access_token)
        if token_data is None:
            TOKEN_VALIDATIONS.labels(status="invalid").inc()
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = fake_users_db.get(token_data.email)
        if not user:
            TOKEN_VALIDATIONS.labels(status="user_not_found").inc()
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        TOKEN_VALIDATIONS.labels(status="valid").inc()
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get current user failed", error=str(e))
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    try:
        # Obter token do cookie
        access_token = get_cookie_from_request(request, "access_token")
        if access_token:
            token_data = verify_token(access_token)
            if token_data:
                user = fake_users_db.get(token_data.email)
                if user and redis_client:
                    # Remover refresh token do Redis
                    redis_client.delete(f"refresh_token:{user['id']}")
                    logger.info("User logged out", email=user["email"], user_id=user["id"])
        
        # Limpar cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        return {"message": "Logout realizado com sucesso"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        # Mesmo com erro, limpar cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return {"message": "Logout realizado com sucesso"}

# Middleware de autenticação para outros serviços
@app.post("/api/auth/validate")
async def validate_token_for_services(request: Request):
    try:
        # Obter token do cookie ou header
        access_token = get_cookie_from_request(request, "access_token")
        if not access_token:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Token não fornecido")
        
        token_data = verify_token(access_token)
        if token_data is None:
            TOKEN_VALIDATIONS.labels(status="invalid").inc()
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = fake_users_db.get(token_data.email)
        if not user:
            TOKEN_VALIDATIONS.labels(status="user_not_found").inc()
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        TOKEN_VALIDATIONS.labels(status="valid").inc()
        
        return {
            "valid": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "is_active": user["is_active"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token validation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Erro na validação do token")

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=None  # Usar structlog
    )

