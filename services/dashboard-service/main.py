"""
Serviço de Dashboards - Agente Investidor
Responsável por gerar visualizações interativas e dashboards personalizáveis
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
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
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
REQUEST_COUNT = Counter('dashboard_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('dashboard_request_duration_seconds', 'Request duration')
CHART_GENERATIONS = Counter('chart_generations_total', 'Chart generations', ['type'])

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=5,  # DB específico para dashboards
    decode_responses=True
)

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Dashboard Service",
    description="Serviço de Dashboards e Visualizações",
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
class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Dict[str, Any] = Field(default_factory=dict)

class Dashboard(BaseModel):
    dashboard_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    layout: Dict[str, Any] = Field(default_factory=dict)
    widgets: List[Dict[str, Any]] = Field(default_factory=list)
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Widget(BaseModel):
    widget_id: str
    dashboard_id: str
    widget_type: str  # chart, table, metric, alert, news
    title: str
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any] = Field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PortfolioMetric(BaseModel):
    total_value: float
    total_change: float
    total_change_percent: float
    daily_change: float
    daily_change_percent: float
    currency: str = "BRL"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PerformanceData(BaseModel):
    period: str  # 1d, 1w, 1m, 3m, 6m, 1y
    dates: List[str]
    values: List[float]
    benchmark_values: Optional[List[float]] = None
    currency: str = "BRL"

# Utility functions
def get_cache_key(prefix: str, **kwargs) -> str:
    """Gerar chave de cache"""
    key_parts = [prefix]
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

async def fetch_data_from_service(service_url: str, endpoint: str) -> Optional[Dict[str, Any]]:
    """Buscar dados de outros serviços"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{service_url}{endpoint}")
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        logger.error("Error fetching data from service", service_url=service_url, endpoint=endpoint, error=str(e))
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
            "service": "dashboard-service",
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

# Dashboard endpoints
@app.get("/dashboards/{user_id}", response_model=List[Dashboard])
async def get_user_dashboards(user_id: str):
    """Obter dashboards do usuário"""
    try:
        cache_key = get_cache_key("dashboards", user_id=user_id)
        cached_dashboards = get_cached_data(cache_key)
        
        if cached_dashboards:
            return [Dashboard(**dashboard) for dashboard in cached_dashboards]
        
        # Dashboards padrão
        default_dashboards = [
            {
                "dashboard_id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Portfolio Overview",
                "description": "Visão geral do portfólio de investimentos",
                "layout": {"columns": 12, "rows": 8},
                "widgets": [],
                "is_public": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "dashboard_id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Market Analysis",
                "description": "Análises de mercado e tendências",
                "layout": {"columns": 12, "rows": 6},
                "widgets": [],
                "is_public": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        cache_data(cache_key, default_dashboards, 1800)
        
        return [Dashboard(**dashboard) for dashboard in default_dashboards]
        
    except Exception as e:
        logger.error("Error getting user dashboards", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/dashboards", response_model=Dashboard)
async def create_dashboard(dashboard: Dashboard):
    """Criar novo dashboard"""
    try:
        dashboard.dashboard_id = str(uuid.uuid4())
        dashboard.created_at = datetime.utcnow()
        dashboard.updated_at = datetime.utcnow()
        
        # Adicionar ao cache
        cache_key = get_cache_key("dashboards", user_id=dashboard.user_id)
        cached_dashboards = get_cached_data(cache_key) or []
        cached_dashboards.append(dashboard.dict())
        cache_data(cache_key, cached_dashboards, 1800)
        
        return dashboard
        
    except Exception as e:
        logger.error("Error creating dashboard", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/dashboards/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(dashboard_id: str, dashboard: Dashboard):
    """Atualizar dashboard"""
    try:
        dashboard.dashboard_id = dashboard_id
        dashboard.updated_at = datetime.utcnow()
        
        # Atualizar no cache
        cache_key = get_cache_key("dashboards", user_id=dashboard.user_id)
        cached_dashboards = get_cached_data(cache_key) or []
        
        for i, cached_dashboard in enumerate(cached_dashboards):
            if cached_dashboard["dashboard_id"] == dashboard_id:
                cached_dashboards[i] = dashboard.dict()
                break
        
        cache_data(cache_key, cached_dashboards, 1800)
        
        return dashboard
        
    except Exception as e:
        logger.error("Error updating dashboard", dashboard_id=dashboard_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str, user_id: str):
    """Deletar dashboard"""
    try:
        # Remover do cache
        cache_key = get_cache_key("dashboards", user_id=user_id)
        cached_dashboards = get_cached_data(cache_key) or []
        
        cached_dashboards = [d for d in cached_dashboards if d["dashboard_id"] != dashboard_id]
        cache_data(cache_key, cached_dashboards, 1800)
        
        return {"status": "success", "message": "Dashboard deleted"}
        
    except Exception as e:
        logger.error("Error deleting dashboard", dashboard_id=dashboard_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Widget endpoints
@app.get("/dashboards/{dashboard_id}/widgets", response_model=List[Widget])
async def get_dashboard_widgets(dashboard_id: str):
    """Obter widgets do dashboard"""
    try:
        cache_key = get_cache_key("widgets", dashboard_id=dashboard_id)
        cached_widgets = get_cached_data(cache_key)
        
        if cached_widgets:
            return [Widget(**widget) for widget in cached_widgets]
        
        # Widgets padrão
        default_widgets = [
            {
                "widget_id": str(uuid.uuid4()),
                "dashboard_id": dashboard_id,
                "widget_type": "metric",
                "title": "Total Portfolio Value",
                "position": {"x": 0, "y": 0, "width": 6, "height": 2},
                "config": {"metric": "total_value", "currency": "BRL"},
                "data": {"value": 100000.0, "change": 2500.0, "change_percent": 2.5},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "widget_id": str(uuid.uuid4()),
                "dashboard_id": dashboard_id,
                "widget_type": "chart",
                "title": "Portfolio Performance",
                "position": {"x": 6, "y": 0, "width": 6, "height": 4},
                "config": {"chart_type": "line", "period": "1y"},
                "data": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "datasets": [{"label": "Portfolio", "data": [95000, 98000, 102000, 105000, 101000, 102500]}]
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        cache_data(cache_key, default_widgets, 1800)
        
        return [Widget(**widget) for widget in default_widgets]
        
    except Exception as e:
        logger.error("Error getting dashboard widgets", dashboard_id=dashboard_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/dashboards/{dashboard_id}/widgets", response_model=Widget)
async def create_widget(dashboard_id: str, widget: Widget):
    """Criar novo widget"""
    try:
        widget.dashboard_id = dashboard_id
        widget.widget_id = str(uuid.uuid4())
        widget.created_at = datetime.utcnow()
        widget.updated_at = datetime.utcnow()
        
        # Adicionar ao cache
        cache_key = get_cache_key("widgets", dashboard_id=dashboard_id)
        cached_widgets = get_cached_data(cache_key) or []
        cached_widgets.append(widget.dict())
        cache_data(cache_key, cached_widgets, 1800)
        
        return widget
        
    except Exception as e:
        logger.error("Error creating widget", dashboard_id=dashboard_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Chart generation endpoints
@app.get("/charts/portfolio-performance/{user_id}", response_model=ChartData)
async def get_portfolio_performance_chart(user_id: str, period: str = "1y"):
    """Gerar gráfico de performance do portfólio"""
    try:
        cache_key = get_cache_key("chart", user_id=user_id, type="performance", period=period)
        cached_chart = get_cached_data(cache_key)
        
        if cached_chart:
            return ChartData(**cached_chart)
        
        # Simular dados de performance
        if period == "1y":
            labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            data = [95000, 98000, 102000, 105000, 101000, 102500, 104000, 106000, 108000, 110000, 112000, 115000]
        elif period == "6m":
            labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            data = [95000, 98000, 102000, 105000, 101000, 102500]
        else:
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri"]
            data = [102000, 102500, 103000, 102800, 103200]
        
        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Portfolio Value",
                    "data": data,
                    "borderColor": "#3498db",
                    "backgroundColor": "rgba(52, 152, 219, 0.1)",
                    "fill": True
                }
            ],
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": False,
                        "ticks": {
                            "callback": "function(value) { return '$' + value.toLocaleString(); }"
                        }
                    }
                }
            }
        }
        
        cache_data(cache_key, chart_data, 1800)
        CHART_GENERATIONS.labels(type="performance").inc()
        
        return ChartData(**chart_data)
        
    except Exception as e:
        logger.error("Error generating performance chart", user_id=user_id, period=period, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/charts/asset-allocation/{user_id}", response_model=ChartData)
async def get_asset_allocation_chart(user_id: str):
    """Gerar gráfico de alocação de ativos"""
    try:
        cache_key = get_cache_key("chart", user_id=user_id, type="allocation")
        cached_chart = get_cached_data(cache_key)
        
        if cached_chart:
            return ChartData(**cached_chart)
        
        # Simular dados de alocação
        chart_data = {
            "labels": ["Stocks", "Bonds", "Real Estate", "Cash", "Commodities"],
            "datasets": [
                {
                    "data": [45, 25, 15, 10, 5],
                    "backgroundColor": [
                        "#3498db", "#e74c3c", "#f39c12", "#27ae60", "#9b59b6"
                    ],
                    "borderWidth": 2,
                    "borderColor": "#fff"
                }
            ],
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {
                        "position": "bottom"
                    }
                }
            }
        }
        
        cache_data(cache_key, chart_data, 1800)
        CHART_GENERATIONS.labels(type="allocation").inc()
        
        return ChartData(**chart_data)
        
    except Exception as e:
        logger.error("Error generating allocation chart", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/charts/risk-return/{user_id}", response_model=ChartData)
async def get_risk_return_chart(user_id: str):
    """Gerar gráfico de risco vs retorno"""
    try:
        cache_key = get_cache_key("chart", user_id=user_id, type="risk_return")
        cached_chart = get_cached_data(cache_key)
        
        if cached_chart:
            return ChartData(**cached_chart)
        
        # Simular dados de risco vs retorno
        chart_data = {
            "labels": ["Low Risk", "Medium Risk", "High Risk"],
            "datasets": [
                {
                    "label": "Expected Return (%)",
                    "data": [5, 8, 12],
                    "backgroundColor": "rgba(52, 152, 219, 0.8)",
                    "borderColor": "#3498db",
                    "borderWidth": 2
                },
                {
                    "label": "Risk Level (%)",
                    "data": [3, 6, 15],
                    "backgroundColor": "rgba(231, 76, 60, 0.8)",
                    "borderColor": "#e74c3c",
                    "borderWidth": 2
                }
            ],
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "Percentage (%)"
                        }
                    }
                }
            }
        }
        
        cache_data(cache_key, chart_data, 1800)
        CHART_GENERATIONS.labels(type="risk_return").inc()
        
        return ChartData(**chart_data)
        
    except Exception as e:
        logger.error("Error generating risk-return chart", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Portfolio metrics endpoints
@app.get("/metrics/portfolio/{user_id}", response_model=PortfolioMetric)
async def get_portfolio_metrics(user_id: str):
    """Obter métricas do portfólio"""
    try:
        cache_key = get_cache_key("portfolio_metrics", user_id=user_id)
        cached_metrics = get_cached_data(cache_key)
        
        if cached_metrics:
            return PortfolioMetric(**cached_metrics)
        
        # Simular métricas do portfólio
        metrics_data = {
            "total_value": 115000.0,
            "total_change": 15000.0,
            "total_change_percent": 15.0,
            "daily_change": 2500.0,
            "daily_change_percent": 2.22,
            "currency": "BRL",
            "last_updated": datetime.utcnow()
        }
        
        cache_data(cache_key, metrics_data, 300)  # 5 minutos
        
        return PortfolioMetric(**metrics_data)
        
    except Exception as e:
        logger.error("Error getting portfolio metrics", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Performance data endpoints
@app.get("/performance/{user_id}", response_model=PerformanceData)
async def get_performance_data(user_id: str, period: str = "1y"):
    """Obter dados de performance"""
    try:
        cache_key = get_cache_key("performance", user_id=user_id, period=period)
        cached_performance = get_cached_data(cache_key)
        
        if cached_performance:
            return PerformanceData(**cached_performance)
        
        # Simular dados de performance
        if period == "1y":
            dates = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", 
                    "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
            values = [95000, 98000, 102000, 105000, 101000, 102500, 104000, 106000, 108000, 110000, 112000, 115000]
            benchmark = [94000, 97000, 101000, 104000, 100000, 101500, 103000, 105000, 107000, 109000, 111000, 114000]
        elif period == "6m":
            dates = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
            values = [104000, 106000, 108000, 110000, 112000, 115000]
            benchmark = [103000, 105000, 107000, 109000, 111000, 114000]
        else:
            dates = ["2024-12-01", "2024-12-02", "2024-12-03", "2024-12-04", "2024-12-05"]
            values = [112000, 112500, 113000, 112800, 113200]
            benchmark = [111000, 111500, 112000, 111800, 112200]
        
        performance_data = {
            "period": period,
            "dates": dates,
            "values": values,
            "benchmark_values": benchmark,
            "currency": "BRL"
        }
        
        cache_data(cache_key, performance_data, 1800)
        
        return PerformanceData(**performance_data)
        
    except Exception as e:
        logger.error("Error getting performance data", user_id=user_id, period=period, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006) 