"""
Serviço de Autenticação OAuth 2.0 - Agente Investidor
Responsável por autenticação OAuth 2.0, JWT, registro e login
"""

import os
import sys
import uvicorn
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import secrets
import hashlib

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import redis
import json
import httpx
import structlog
from prometheus_client import Counter, Histogram, generate_latest, start_http_server
import time

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

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/auth_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# OAuth 2.0 Providers
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

# Métricas Prometheus
REQUEST_COUNT = Counter('auth_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('auth_request_duration_seconds', 'Request duration')
LOGIN_COUNT = Counter('auth_login_total', 'Total logins', ['provider'])
REGISTRATION_COUNT = Counter('auth_registration_total', 'Total registrations')

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Conectado ao Redis com sucesso")
except Exception as e:
    logger.error(f"Erro ao conectar ao Redis: {e}")
    redis_client = None

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # Nullable para OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth fields
    provider = Column(String, nullable=True)  # google, github, local
    provider_id = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class OAuthState(Base):
    __tablename__ = "oauth_states"
    
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    provider: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenRefresh(BaseModel):
    refresh_token: str

# FastAPI app
app = FastAPI(
    title="Authentication Service OAuth 2.0",
    description="Serviço de Autenticação OAuth 2.0 Completo",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth setup
oauth = OAuth()

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    oauth.register(
        name='github',
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int, db: Session) -> str:
    # Generate secure random token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store in database
    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def generate_oauth_state(provider: str, redirect_uri: Optional[str], db: Session) -> str:
    state = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes
    
    db_state = OAuthState(
        state=state,
        provider=provider,
        redirect_uri=redirect_uri,
        expires_at=expires_at
    )
    db.add(db_state)
    db.commit()
    
    return state

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
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

# Endpoints

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "auth-service-oauth",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "redis_connected": redis_client is not None,
        "oauth_providers": {
            "google": bool(GOOGLE_CLIENT_ID),
            "github": bool(GITHUB_CLIENT_ID)
        }
    }

@app.get("/metrics")
async def get_metrics():
    return generate_latest()

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registra novo usuário"""
    try:
        # Verificar se usuário já existe
        existing_user = db.query(User).filter(
            (User.email == user.email) | (User.username == user.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email ou username já cadastrado"
            )
        
        # Criar usuário
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            provider="local"
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        REGISTRATION_COUNT.inc()
        logger.info(f"Usuário registrado: {user.email}")
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            provider=db_user.provider,
            avatar_url=db_user.avatar_url,
            created_at=db_user.created_at
        )
        
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login com email e senha"""
    try:
        # Verificar usuário
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
        
        if not db_user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Conta desativada"
            )
        
        # Criar tokens
        access_token = create_access_token(data={"sub": db_user.id})
        refresh_token = create_refresh_token(db_user.id, db)
        
        LOGIN_COUNT.labels(provider="local").inc()
        logger.info(f"Login realizado: {user.email}")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token"""
    try:
        # Verificar refresh token
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == token_data.refresh_token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=401,
                detail="Refresh token inválido ou expirado"
            )
        
        # Buscar usuário
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Usuário não encontrado ou inativo"
            )
        
        # Revogar token antigo
        db_token.is_revoked = True
        
        # Criar novos tokens
        access_token = create_access_token(data={"sub": user.id})
        new_refresh_token = create_refresh_token(user.id, db)
        
        db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request, redirect_uri: Optional[str] = None, db: Session = Depends(get_db)):
    """Inicia fluxo OAuth 2.0"""
    try:
        if provider not in ['google', 'github']:
            raise HTTPException(status_code=400, detail="Provider não suportado")
        
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(status_code=400, detail=f"Provider {provider} não configurado")
        
        # Gerar state para CSRF protection
        state = generate_oauth_state(provider, redirect_uri, db)
        
        # Redirect URI para callback
        callback_uri = request.url_for('oauth_callback', provider=provider)
        
        return await client.authorize_redirect(request, callback_uri, state=state)
        
    except Exception as e:
        logger.error(f"Erro no OAuth login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Callback OAuth 2.0"""
    try:
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(status_code=400, detail=f"Provider {provider} não configurado")
        
        # Verificar state
        state = request.query_params.get('state')
        if not state:
            raise HTTPException(status_code=400, detail="State missing")
        
        db_state = db.query(OAuthState).filter(
            OAuthState.state == state,
            OAuthState.provider == provider,
            OAuthState.expires_at > datetime.utcnow()
        ).first()
        
        if not db_state:
            raise HTTPException(status_code=400, detail="State inválido ou expirado")
        
        # Trocar code por token
        token = await client.authorize_access_token(request)
        
        # Buscar dados do usuário
        if provider == 'google':
            user_info = token.get('userinfo')
            if not user_info:
                user_info = await client.parse_id_token(token)
            
            email = user_info.get('email')
            name = user_info.get('name')
            provider_id = user_info.get('sub')
            avatar_url = user_info.get('picture')
            
        elif provider == 'github':
            resp = await client.get('user', token=token)
            user_info = resp.json()
            
            email = user_info.get('email')
            name = user_info.get('name') or user_info.get('login')
            provider_id = str(user_info.get('id'))
            avatar_url = user_info.get('avatar_url')
            
            # GitHub pode não retornar email público
            if not email:
                resp = await client.get('user/emails', token=token)
                emails = resp.json()
                primary_email = next((e for e in emails if e.get('primary')), None)
                if primary_email:
                    email = primary_email.get('email')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email não disponível")
        
        # Buscar ou criar usuário
        user = db.query(User).filter(
            (User.email == email) | 
            ((User.provider == provider) & (User.provider_id == provider_id))
        ).first()
        
        if not user:
            # Criar novo usuário
            username = email.split('@')[0]
            # Garantir username único
            counter = 1
            original_username = username
            while db.query(User).filter(User.username == username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User(
                email=email,
                username=username,
                full_name=name,
                provider=provider,
                provider_id=provider_id,
                avatar_url=avatar_url,
                is_verified=True  # OAuth users são considerados verificados
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            REGISTRATION_COUNT.inc()
            logger.info(f"Usuário OAuth criado: {email}")
        
        else:
            # Atualizar dados existentes
            user.full_name = name or user.full_name
            user.avatar_url = avatar_url or user.avatar_url
            user.is_verified = True
            db.commit()
        
        # Criar tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(user.id, db)
        
        LOGIN_COUNT.labels(provider=provider).inc()
        logger.info(f"Login OAuth realizado: {email}")
        
        # Limpar state usado
        db.delete(db_state)
        db.commit()
        
        # Redirect com tokens (em produção, usar redirect seguro)
        redirect_uri = db_state.redirect_uri or "http://localhost:3000/auth/callback"
        return RedirectResponse(
            url=f"{redirect_uri}?access_token={access_token}&refresh_token={refresh_token}&token_type=bearer"
        )
        
    except OAuthError as e:
        logger.error(f"Erro OAuth: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no callback OAuth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        provider=current_user.provider,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )

@app.post("/logout")
async def logout(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Logout - revoga refresh token"""
    try:
        # Revogar refresh token
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == token_data.refresh_token
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db.commit()
        
        return {"message": "Logout realizado com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validate")
async def validate_token(current_user: User = Depends(get_current_user)):
    """Valida token de acesso"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=None  # Usar nosso logging estruturado
    )

