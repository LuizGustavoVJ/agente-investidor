"""
Serviço de Dados Externos - Agente Investidor
Responsável por integração com APIs externas, cache e normalização de dados
Integrado com frontend Vue.js
"""

import os
import uvicorn
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import structlog
import time
import redis
import json
import httpx
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio
from asyncio_throttle import Throttler

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
REQUEST_COUNT = Counter('data_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('data_request_duration_seconds', 'Request duration')
CACHE_HITS = Counter('data_cache_hits_total', 'Cache hits', ['level', 'key_type'])
CACHE_MISSES = Counter('data_cache_misses_total', 'Cache misses', ['level', 'key_type'])
API_CALLS = Counter('data_external_api_calls_total', 'External API calls', ['provider', 'status'])

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
            db=1,  # Database separado para dados
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

# Rate limiting
throttler = Throttler(rate_limit=10, period=1)  # 10 requests per second

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Data Service",
    description="Serviço de Dados Externos integrado com Frontend Vue.js",
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

# Models
class StockData(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    timestamp: datetime

class HistoricalData(BaseModel):
    symbol: str
    period: str
    data: List[Dict[str, Any]]

class MarketSummary(BaseModel):
    indices: Dict[str, Dict[str, Any]]
    top_gainers: List[StockData]
    top_losers: List[StockData]
    most_active: List[StockData]
    timestamp: datetime

class PortfolioData(BaseModel):
    symbols: List[str]
    total_value: float
    total_change: float
    total_change_percent: float
    positions: List[Dict[str, Any]]
    timestamp: datetime

# Utility functions
async def verify_auth_token(request: Request):
    """Verificar token de autenticação com auth service"""
    try:
        # Obter token do cookie ou header
        access_token = request.cookies.get("access_token")
        if not access_token:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
        
        if not access_token:
            return None
        
        # Validar com auth service
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
    """Gerar chave de cache"""
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"

def cache_get(key: str) -> Optional[Any]:
    """Obter dados do cache"""
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            CACHE_HITS.labels(level="redis", key_type=key.split(":")[0]).inc()
            return json.loads(data)
        CACHE_MISSES.labels(level="redis", key_type=key.split(":")[0]).inc()
        return None
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
        return None

def cache_set(key: str, data: Any, ttl: int = 300):
    """Salvar dados no cache"""
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(data, default=str))
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")

async def fetch_stock_data(symbol: str) -> Optional[StockData]:
    """Buscar dados de ação"""
    try:
        async with throttler:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100 if prev_price != 0 else 0
            
            API_CALLS.labels(provider="yfinance", status="success").inc()
            
            return StockData(
                symbol=symbol,
                name=info.get('longName', symbol),
                price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                timestamp=datetime.utcnow()
            )
    except Exception as e:
        API_CALLS.labels(provider="yfinance", status="error").inc()
        logger.error(f"Failed to fetch stock data for {symbol}: {e}")
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
        redis_status = "healthy"
        if redis_client:
            redis_client.ping()
        else:
            redis_status = "unavailable"
            
        return {
            "status": "healthy",
            "service": "data-service",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "redis": redis_status,
                "yfinance": "available"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Métricas endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Data endpoints
@app.get("/api/data/stock/{symbol}", response_model=StockData)
async def get_stock_data(symbol: str, request: Request):
    """Obter dados de uma ação específica"""
    try:
        # Verificar cache primeiro
        cache_key = get_cache_key("stock", symbol.upper())
        cached_data = cache_get(cache_key)
        
        if cached_data:
            return StockData(**cached_data)
        
        # Buscar dados externos
        stock_data = await fetch_stock_data(symbol.upper())
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Dados não encontrados para {symbol}")
        
        # Salvar no cache (5 minutos)
        cache_set(cache_key, stock_data.dict(), ttl=300)
        
        return stock_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stock data: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/data/stocks/batch", response_model=List[StockData])
async def get_multiple_stocks(symbols: str = Query(..., description="Símbolos separados por vírgula")):
    """Obter dados de múltiplas ações"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        results = []
        
        # Processar em paralelo com limite
        semaphore = asyncio.Semaphore(5)  # Máximo 5 requisições simultâneas
        
        async def fetch_with_semaphore(symbol):
            async with semaphore:
                return await fetch_stock_data(symbol)
        
        tasks = [fetch_with_semaphore(symbol) for symbol in symbol_list]
        stock_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for data in stock_data_list:
            if isinstance(data, StockData):
                results.append(data)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get multiple stocks: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/data/historical/{symbol}", response_model=HistoricalData)
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="Período: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """Obter dados históricos de uma ação"""
    try:
        cache_key = get_cache_key("historical", symbol.upper(), period, interval)
        cached_data = cache_get(cache_key)
        
        if cached_data:
            return HistoricalData(**cached_data)
        
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Dados históricos não encontrados para {symbol}")
        
        # Converter para formato JSON
        data = []
        for index, row in hist.iterrows():
            data.append({
                "date": index.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        result = HistoricalData(
            symbol=symbol.upper(),
            period=period,
            data=data
        )
        
        # Cache por 1 hora para dados históricos
        cache_set(cache_key, result.dict(), ttl=3600)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get historical data: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/data/market-summary", response_model=MarketSummary)
async def get_market_summary():
    """Obter resumo do mercado"""
    try:
        cache_key = get_cache_key("market_summary")
        cached_data = cache_get(cache_key)
        
        if cached_data:
            return MarketSummary(**cached_data)
        
        # Índices principais
        indices_symbols = {
            "IBOV": "^BVSP",
            "S&P500": "^GSPC", 
            "NASDAQ": "^IXIC",
            "DOW": "^DJI"
        }
        
        indices = {}
        for name, symbol in indices_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev
                    change_percent = (change / prev) * 100 if prev != 0 else 0
                    
                    indices[name] = {
                        "value": float(current),
                        "change": float(change),
                        "change_percent": float(change_percent)
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch index {name}: {e}")
        
        # Top gainers/losers (simulado - em produção usar API específica)
        top_gainers = []
        top_losers = []
        most_active = []
        
        # Ações brasileiras populares para exemplo
        popular_stocks = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"]
        
        for symbol in popular_stocks:
            stock_data = await fetch_stock_data(symbol)
            if stock_data:
                if stock_data.change_percent > 0:
                    top_gainers.append(stock_data)
                else:
                    top_losers.append(stock_data)
                most_active.append(stock_data)
        
        # Ordenar listas
        top_gainers.sort(key=lambda x: x.change_percent, reverse=True)
        top_losers.sort(key=lambda x: x.change_percent)
        most_active.sort(key=lambda x: x.volume, reverse=True)
        
        result = MarketSummary(
            indices=indices,
            top_gainers=top_gainers[:5],
            top_losers=top_losers[:5],
            most_active=most_active[:5],
            timestamp=datetime.utcnow()
        )
        
        # Cache por 5 minutos
        cache_set(cache_key, result.dict(), ttl=300)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get market summary: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/data/portfolio", response_model=PortfolioData)
async def get_portfolio_data(symbols: List[str], request: Request):
    """Obter dados consolidados de portfolio (requer autenticação)"""
    try:
        # Verificar autenticação
        user = await verify_auth_token(request)
        if not user:
            raise HTTPException(status_code=401, detail="Autenticação necessária")
        
        # Buscar dados de todas as ações
        portfolio_stocks = []
        total_value = 0
        total_change = 0
        
        for symbol in symbols:
            stock_data = await fetch_stock_data(symbol.upper())
            if stock_data:
                portfolio_stocks.append({
                    "symbol": stock_data.symbol,
                    "name": stock_data.name,
                    "price": stock_data.price,
                    "change": stock_data.change,
                    "change_percent": stock_data.change_percent,
                    "volume": stock_data.volume
                })
                # Assumindo 1 ação de cada (em produção, usar quantidades reais)
                total_value += stock_data.price
                total_change += stock_data.change
        
        total_change_percent = (total_change / (total_value - total_change)) * 100 if total_value != total_change else 0
        
        return PortfolioData(
            symbols=symbols,
            total_value=total_value,
            total_change=total_change,
            total_change_percent=total_change_percent,
            positions=portfolio_stocks,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get portfolio data: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/data/search")
async def search_stocks(q: str = Query(..., description="Termo de busca")):
    """Buscar ações por nome ou símbolo"""
    try:
        # Cache de busca
        cache_key = get_cache_key("search", q.lower())
        cached_data = cache_get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Lista simplificada de ações brasileiras (em produção, usar API de busca)
        brazilian_stocks = {
            "PETR4.SA": "Petróleo Brasileiro S.A. - Petrobras",
            "VALE3.SA": "Vale S.A.",
            "ITUB4.SA": "Itaú Unibanco Holding S.A.",
            "BBDC4.SA": "Banco Bradesco S.A.",
            "ABEV3.SA": "Ambev S.A.",
            "WEGE3.SA": "WEG S.A.",
            "RENT3.SA": "Localiza Rent a Car S.A.",
            "LREN3.SA": "Lojas Renner S.A.",
            "MGLU3.SA": "Magazine Luiza S.A.",
            "JBSS3.SA": "JBS S.A."
        }
        
        results = []
        query_lower = q.lower()
        
        for symbol, name in brazilian_stocks.items():
            if query_lower in symbol.lower() or query_lower in name.lower():
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "type": "stock"
                })
        
        # Cache por 1 hora
        cache_set(cache_key, results, ttl=3600)
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search stocks: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_config=None  # Usar structlog
    )

