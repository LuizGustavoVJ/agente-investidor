"""
Serviço de Usuários - Agente Investidor
Responsável por gestão de usuários, portfolios e configurações
Integrado com frontend Vue.js
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import structlog
import time
import redis
import json
import httpx
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from enum import Enum

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
REQUEST_COUNT = Counter('user_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('user_request_duration_seconds', 'Request duration')
PORTFOLIO_OPERATIONS = Counter('user_portfolio_operations_total', 'Portfolio operations', ['operation', 'status'])

# Frontend URLs para CORS
FRONTEND_URLS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080", 
    "https://agente-investidor-frontend.vercel.app",
    "https://agenteinvestidor.com"
]

# Redis connection
def get_redis_client():
    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=3,  # Database separado para usuários
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

# FastAPI app
app = FastAPI(
    title="Agente Investidor - User Service",
    description="Serviço de Usuários integrado com Frontend Vue.js",
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

# Enums
class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class InvestmentGoal(str, Enum):
    RETIREMENT = "retirement"
    HOUSE = "house"
    EDUCATION = "education"
    EMERGENCY = "emergency"
    TRAVEL = "travel"
    OTHER = "other"

# Models
class UserProfile(BaseModel):
    user_id: str
    risk_profile: RiskProfile
    investment_goals: List[InvestmentGoal]
    monthly_income: Optional[float] = None
    monthly_investment: Optional[float] = None
    investment_horizon: Optional[int] = None  # em anos
    experience_level: Optional[str] = None
    updated_at: datetime

class PortfolioAsset(BaseModel):
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    gain_loss: Optional[float] = None
    gain_loss_percent: Optional[float] = None
    weight: Optional[float] = None
    added_at: datetime

class Portfolio(BaseModel):
    user_id: str
    assets: List[PortfolioAsset]
    total_value: float
    total_invested: float
    total_gain_loss: float
    total_gain_loss_percent: float
    last_updated: datetime

class Goal(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float
    target_date: datetime
    category: InvestmentGoal
    priority: str  # high, medium, low
    status: str  # active, completed, paused
    created_at: datetime
    updated_at: datetime

class Broker(BaseModel):
    id: str
    user_id: str
    name: str
    api_key: Optional[str] = None
    is_connected: bool
    last_sync: Optional[datetime] = None
    sync_status: str  # connected, error, syncing
    assets_count: int
    total_value: float
    created_at: datetime

# Utility functions
async def verify_auth_token(request: Request):
    """Verificar token de autenticação com auth service"""
    try:
        access_token = request.cookies.get("access_token")
        if not access_token:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
        
        if not access_token:
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{os.getenv('AUTH_SERVICE_HOST', 'auth-service')}:8001/api/auth/validate",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()["user"]
            return None
    except Exception as e:
        logger.warning(f"Auth verification failed: {e}")
        return None

def get_cache_key(prefix: str, *args) -> str:
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"

def cache_get(key: str) -> Optional[Any]:
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
        return None

def cache_set(key: str, data: Any, ttl: int = 3600):
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(data, default=str))
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")

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
        redis_status = "healthy"
        if redis_client:
            redis_client.ping()
        else:
            redis_status = "unavailable"
            
        return {
            "status": "healthy",
            "service": "user-service",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "redis": redis_status
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Simulated databases
fake_profiles_db = {}
fake_portfolios_db = {}
fake_goals_db = {}
fake_brokers_db = {}

# User Profile endpoints
@app.get("/api/user/profile", response_model=UserProfile)
async def get_user_profile(request: Request):
    """Obter perfil do usuário"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        profile = fake_profiles_db.get(user["id"])
        if not profile:
            # Criar perfil padrão
            profile = {
                "user_id": user["id"],
                "risk_profile": RiskProfile.MODERATE,
                "investment_goals": [InvestmentGoal.RETIREMENT],
                "monthly_income": None,
                "monthly_investment": None,
                "investment_horizon": None,
                "experience_level": "beginner",
                "updated_at": datetime.utcnow()
            }
            fake_profiles_db[user["id"]] = profile
        
        return UserProfile(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.put("/api/user/profile", response_model=UserProfile)
async def update_user_profile(profile_data: dict, request: Request):
    """Atualizar perfil do usuário"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        profile_data["user_id"] = user["id"]
        profile_data["updated_at"] = datetime.utcnow()
        
        fake_profiles_db[user["id"]] = profile_data
        
        return UserProfile(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Portfolio endpoints
@app.get("/api/user/portfolio", response_model=Portfolio)
async def get_user_portfolio(request: Request):
    """Obter portfolio do usuário"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        portfolio = fake_portfolios_db.get(user["id"])
        if not portfolio:
            # Criar portfolio vazio
            portfolio = {
                "user_id": user["id"],
                "assets": [],
                "total_value": 0.0,
                "total_invested": 0.0,
                "total_gain_loss": 0.0,
                "total_gain_loss_percent": 0.0,
                "last_updated": datetime.utcnow()
            }
            fake_portfolios_db[user["id"]] = portfolio
        
        return Portfolio(**portfolio)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user portfolio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/user/portfolio/assets")
async def add_portfolio_asset(asset_data: dict, request: Request):
    """Adicionar ativo ao portfolio"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        portfolio = fake_portfolios_db.get(user["id"], {
            "user_id": user["id"],
            "assets": [],
            "total_value": 0.0,
            "total_invested": 0.0,
            "total_gain_loss": 0.0,
            "total_gain_loss_percent": 0.0,
            "last_updated": datetime.utcnow()
        })
        
        # Adicionar novo ativo
        new_asset = {
            **asset_data,
            "added_at": datetime.utcnow()
        }
        portfolio["assets"].append(new_asset)
        portfolio["last_updated"] = datetime.utcnow()
        
        # Recalcular totais (simplificado)
        total_invested = sum(asset["quantity"] * asset["average_price"] for asset in portfolio["assets"])
        portfolio["total_invested"] = total_invested
        
        fake_portfolios_db[user["id"]] = portfolio
        
        PORTFOLIO_OPERATIONS.labels(operation="add_asset", status="success").inc()
        
        return {"message": "Ativo adicionado com sucesso", "asset": new_asset}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add portfolio asset: {e}")
        PORTFOLIO_OPERATIONS.labels(operation="add_asset", status="error").inc()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Goals endpoints
@app.get("/api/user/goals", response_model=List[Goal])
async def get_user_goals(request: Request):
    """Obter metas do usuário"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        user_goals = [goal for goal in fake_goals_db.values() if goal["user_id"] == user["id"]]
        
        return [Goal(**goal) for goal in user_goals]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user goals: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/user/goals", response_model=Goal)
async def create_goal(goal_data: dict, request: Request):
    """Criar nova meta"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        goal_id = f"goal_{len(fake_goals_db) + 1}"
        goal = {
            "id": goal_id,
            "user_id": user["id"],
            **goal_data,
            "current_amount": 0.0,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        fake_goals_db[goal_id] = goal
        
        return Goal(**goal)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create goal: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.put("/api/user/goals/{goal_id}", response_model=Goal)
async def update_goal(goal_id: str, goal_data: dict, request: Request):
    """Atualizar meta"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        goal = fake_goals_db.get(goal_id)
        if not goal or goal["user_id"] != user["id"]:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        goal.update(goal_data)
        goal["updated_at"] = datetime.utcnow()
        
        fake_goals_db[goal_id] = goal
        
        return Goal(**goal)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update goal: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Brokers endpoints
@app.get("/api/user/brokers", response_model=List[Broker])
async def get_user_brokers(request: Request):
    """Obter corretoras do usuário"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        user_brokers = [broker for broker in fake_brokers_db.values() if broker["user_id"] == user["id"]]
        
        return [Broker(**broker) for broker in user_brokers]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user brokers: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/user/brokers", response_model=Broker)
async def add_broker(broker_data: dict, request: Request):
    """Adicionar corretora"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        broker_id = f"broker_{len(fake_brokers_db) + 1}"
        broker = {
            "id": broker_id,
            "user_id": user["id"],
            **broker_data,
            "is_connected": False,
            "last_sync": None,
            "sync_status": "disconnected",
            "assets_count": 0,
            "total_value": 0.0,
            "created_at": datetime.utcnow()
        }
        
        fake_brokers_db[broker_id] = broker
        
        return Broker(**broker)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add broker: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/user/brokers/{broker_id}/sync")
async def sync_broker(broker_id: str, request: Request):
    """Sincronizar dados da corretora"""
    try:
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        broker = fake_brokers_db.get(broker_id)
        if not broker or broker["user_id"] != user["id"]:
            raise HTTPException(status_code=404, detail="Corretora não encontrada")
        
        # Simular sincronização
        broker["sync_status"] = "syncing"
        broker["last_sync"] = datetime.utcnow()
        broker["is_connected"] = True
        broker["assets_count"] = 5  # Simulado
        broker["total_value"] = 50000.0  # Simulado
        
        fake_brokers_db[broker_id] = broker
        
        return {"message": "Sincronização iniciada", "status": "syncing"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync broker: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_config=None  # Usar structlog
    )

