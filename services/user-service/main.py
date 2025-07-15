"""
Serviço de Usuários - Agente Investidor
Responsável por gerenciamento de perfis, preferências e configurações de usuários
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import start_http_server
import structlog
import time
import redis
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
import uuid

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
PROFILE_UPDATES = Counter('user_profile_updates_total', 'Profile updates', ['type'])

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=4,  # DB específico para usuários
    decode_responses=True
)

# FastAPI app
app = FastAPI(
    title="Agente Investidor - User Service",
    description="Serviço de Gerenciamento de Usuários",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "pt-BR"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserPreferences(BaseModel):
    user_id: str
    theme: str = "light"  # light, dark, auto
    notifications_enabled: bool = True
    email_notifications: bool = True
    push_notifications: bool = False
    sms_notifications: bool = False
    dashboard_layout: Dict[str, Any] = Field(default_factory=dict)
    default_methodologies: List[str] = Field(default_factory=list)
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    investment_horizon: str = "medium"  # short, medium, long
    preferred_currencies: List[str] = Field(default_factory=lambda: ["BRL", "USD"])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSettings(BaseModel):
    user_id: str
    privacy_level: str = "standard"  # public, standard, private
    data_sharing: bool = False
    analytics_tracking: bool = True
    auto_backup: bool = True
    two_factor_auth: bool = False
    session_timeout: int = 3600  # segundos
    max_sessions: int = 5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserActivity(BaseModel):
    user_id: str
    activity_type: str  # login, analysis, report, dashboard_view
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DashboardWidget(BaseModel):
    widget_id: str
    user_id: str
    widget_type: str  # chart, table, metric, alert
    title: str
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def get_cache_key(prefix: str, user_id: str, **kwargs) -> str:
    """Gerar chave de cache"""
    key_parts = [prefix, user_id]
    for k, v in kwargs.items():
        key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)

def cache_data(key: str, data: Any, ttl: int = 1800):
    """Salvar dados no cache"""
    try:
        redis_client.setex(key, ttl, json.dumps(data, default=str))
    except Exception as e:
        logger.error("Cache save failed", key=key, error=str(e))

def get_cached_data(key: str) -> Optional[Any]:
    """Recuperar dados do cache"""
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error("Cache read failed", key=key, error=str(e))
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
            "service": "user-service",
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

# User Profile endpoints
@app.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Obter perfil do usuário"""
    try:
        cache_key = get_cache_key("profile", user_id)
        cached_profile = get_cached_data(cache_key)
        
        if cached_profile:
            return UserProfile(**cached_profile)
        
        # Simular dados do usuário (em produção, viria do banco)
        profile_data = {
            "user_id": user_id,
            "email": f"user_{user_id}@example.com",
            "first_name": "Usuário",
            "last_name": "Exemplo",
            "phone": "+55 11 99999-9999",
            "date_of_birth": "1990-01-01",
            "country": "Brasil",
            "timezone": "America/Sao_Paulo",
            "language": "pt-BR",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Cache por 30 minutos
        cache_data(cache_key, profile_data, 1800)
        
        return UserProfile(**profile_data)
        
    except Exception as e:
        logger.error("Error getting user profile", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile: UserProfile):
    """Atualizar perfil do usuário"""
    try:
        profile.user_id = user_id
        profile.updated_at = datetime.utcnow()
        
        # Invalidar cache
        cache_key = get_cache_key("profile", user_id)
        redis_client.delete(cache_key)
        
        # Cache novo perfil
        cache_data(cache_key, profile.dict(), 1800)
        
        PROFILE_UPDATES.labels(type="profile").inc()
        
        return profile
        
    except Exception as e:
        logger.error("Error updating user profile", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# User Preferences endpoints
@app.get("/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """Obter preferências do usuário"""
    try:
        cache_key = get_cache_key("preferences", user_id)
        cached_prefs = get_cached_data(cache_key)
        
        if cached_prefs:
            return UserPreferences(**cached_prefs)
        
        # Preferências padrão
        preferences_data = {
            "user_id": user_id,
            "theme": "light",
            "notifications_enabled": True,
            "email_notifications": True,
            "push_notifications": False,
            "sms_notifications": False,
            "dashboard_layout": {
                "widgets": [],
                "columns": 3,
                "rows": 4
            },
            "default_methodologies": ["warren_buffett", "benjamin_graham"],
            "risk_tolerance": "moderate",
            "investment_horizon": "medium",
            "preferred_currencies": ["BRL", "USD"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        cache_data(cache_key, preferences_data, 1800)
        
        return UserPreferences(**preferences_data)
        
    except Exception as e:
        logger.error("Error getting user preferences", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/preferences/{user_id}", response_model=UserPreferences)
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """Atualizar preferências do usuário"""
    try:
        preferences.user_id = user_id
        preferences.updated_at = datetime.utcnow()
        
        # Invalidar cache
        cache_key = get_cache_key("preferences", user_id)
        redis_client.delete(cache_key)
        
        # Cache novas preferências
        cache_data(cache_key, preferences.dict(), 1800)
        
        PROFILE_UPDATES.labels(type="preferences").inc()
        
        return preferences
        
    except Exception as e:
        logger.error("Error updating user preferences", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# User Settings endpoints
@app.get("/settings/{user_id}", response_model=UserSettings)
async def get_user_settings(user_id: str):
    """Obter configurações do usuário"""
    try:
        cache_key = get_cache_key("settings", user_id)
        cached_settings = get_cached_data(cache_key)
        
        if cached_settings:
            return UserSettings(**cached_settings)
        
        # Configurações padrão
        settings_data = {
            "user_id": user_id,
            "privacy_level": "standard",
            "data_sharing": False,
            "analytics_tracking": True,
            "auto_backup": True,
            "two_factor_auth": False,
            "session_timeout": 3600,
            "max_sessions": 5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        cache_data(cache_key, settings_data, 1800)
        
        return UserSettings(**settings_data)
        
    except Exception as e:
        logger.error("Error getting user settings", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/settings/{user_id}", response_model=UserSettings)
async def update_user_settings(user_id: str, settings: UserSettings):
    """Atualizar configurações do usuário"""
    try:
        settings.user_id = user_id
        settings.updated_at = datetime.utcnow()
        
        # Invalidar cache
        cache_key = get_cache_key("settings", user_id)
        redis_client.delete(cache_key)
        
        # Cache novas configurações
        cache_data(cache_key, settings.dict(), 1800)
        
        PROFILE_UPDATES.labels(type="settings").inc()
        
        return settings
        
    except Exception as e:
        logger.error("Error updating user settings", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# User Activity endpoints
@app.post("/activity/{user_id}")
async def log_user_activity(user_id: str, activity: UserActivity):
    """Registrar atividade do usuário"""
    try:
        activity.user_id = user_id
        activity.timestamp = datetime.utcnow()
        
        # Salvar atividade (em produção, seria no banco)
        activity_key = f"activity:{user_id}:{activity.timestamp.timestamp()}"
        cache_data(activity_key, activity.dict(), 86400)  # 24 horas
        
        logger.info("User activity logged", 
                   user_id=user_id, 
                   activity_type=activity.activity_type,
                   description=activity.description)
        
        return {"status": "success", "message": "Activity logged"}
        
    except Exception as e:
        logger.error("Error logging user activity", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/activity/{user_id}", response_model=List[UserActivity])
async def get_user_activities(user_id: str, limit: int = 50):
    """Obter atividades do usuário"""
    try:
        # Buscar atividades do cache (em produção, viria do banco)
        pattern = f"activity:{user_id}:*"
        keys = redis_client.keys(pattern)
        
        activities = []
        for key in keys[:limit]:
            activity_data = get_cached_data(key)
            if activity_data:
                activities.append(UserActivity(**activity_data))
        
        # Ordenar por timestamp (mais recente primeiro)
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        
        return activities
        
    except Exception as e:
        logger.error("Error getting user activities", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Dashboard Widgets endpoints
@app.get("/dashboard/{user_id}/widgets", response_model=List[DashboardWidget])
async def get_user_dashboard_widgets(user_id: str):
    """Obter widgets do dashboard do usuário"""
    try:
        cache_key = get_cache_key("dashboard_widgets", user_id)
        cached_widgets = get_cached_data(cache_key)
        
        if cached_widgets:
            return [DashboardWidget(**widget) for widget in cached_widgets]
        
        # Widgets padrão
        default_widgets = [
            {
                "widget_id": str(uuid.uuid4()),
                "user_id": user_id,
                "widget_type": "metric",
                "title": "Portfolio Value",
                "position": {"x": 0, "y": 0, "width": 6, "height": 2},
                "config": {"metric": "total_value", "currency": "BRL"},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "widget_id": str(uuid.uuid4()),
                "user_id": user_id,
                "widget_type": "chart",
                "title": "Performance Chart",
                "position": {"x": 6, "y": 0, "width": 6, "height": 4},
                "config": {"chart_type": "line", "period": "1y"},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "widget_id": str(uuid.uuid4()),
                "user_id": user_id,
                "widget_type": "table",
                "title": "Top Holdings",
                "position": {"x": 0, "y": 2, "width": 6, "height": 4},
                "config": {"limit": 10, "sort_by": "value"},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        cache_data(cache_key, default_widgets, 1800)
        
        return [DashboardWidget(**widget) for widget in default_widgets]
        
    except Exception as e:
        logger.error("Error getting dashboard widgets", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/dashboard/{user_id}/widgets", response_model=DashboardWidget)
async def create_dashboard_widget(user_id: str, widget: DashboardWidget):
    """Criar novo widget no dashboard"""
    try:
        widget.user_id = user_id
        widget.widget_id = str(uuid.uuid4())
        widget.created_at = datetime.utcnow()
        widget.updated_at = datetime.utcnow()
        
        # Adicionar ao cache
        cache_key = get_cache_key("dashboard_widgets", user_id)
        cached_widgets = get_cached_data(cache_key) or []
        cached_widgets.append(widget.dict())
        cache_data(cache_key, cached_widgets, 1800)
        
        return widget
        
    except Exception as e:
        logger.error("Error creating dashboard widget", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/dashboard/{user_id}/widgets/{widget_id}", response_model=DashboardWidget)
async def update_dashboard_widget(user_id: str, widget_id: str, widget: DashboardWidget):
    """Atualizar widget do dashboard"""
    try:
        widget.user_id = user_id
        widget.widget_id = widget_id
        widget.updated_at = datetime.utcnow()
        
        # Atualizar no cache
        cache_key = get_cache_key("dashboard_widgets", user_id)
        cached_widgets = get_cached_data(cache_key) or []
        
        for i, cached_widget in enumerate(cached_widgets):
            if cached_widget["widget_id"] == widget_id:
                cached_widgets[i] = widget.dict()
                break
        
        cache_data(cache_key, cached_widgets, 1800)
        
        return widget
        
    except Exception as e:
        logger.error("Error updating dashboard widget", user_id=user_id, widget_id=widget_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/dashboard/{user_id}/widgets/{widget_id}")
async def delete_dashboard_widget(user_id: str, widget_id: str):
    """Deletar widget do dashboard"""
    try:
        # Remover do cache
        cache_key = get_cache_key("dashboard_widgets", user_id)
        cached_widgets = get_cached_data(cache_key) or []
        
        cached_widgets = [w for w in cached_widgets if w["widget_id"] != widget_id]
        cache_data(cache_key, cached_widgets, 1800)
        
        return {"status": "success", "message": "Widget deleted"}
        
    except Exception as e:
        logger.error("Error deleting dashboard widget", user_id=user_id, widget_id=widget_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005) 