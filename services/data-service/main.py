"""
Serviço de Dados Externos - Agente Investidor
Responsável por integração com APIs externas, cache e normalização de dados
"""

import os
import uvicorn
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
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
import sys
sys.path.append('/app/microservices')
# Importações de cache (com fallback se não disponível)
try:
    from shared.cache.advanced_cache import cache_hits, cache_misses
except ImportError:
    # Fallback se o módulo não estiver disponível
    from prometheus_client import Counter
    cache_hits = Counter('data_cache_hits_total', 'Cache hits', ['level', 'key_type'])
    cache_misses = Counter('data_cache_misses_total', 'Cache misses', ['level', 'key_type'])

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
API_CALLS = Counter('external_api_calls_total', 'External API calls', ['provider', 'status'])
# Remover as definições duplicadas
# CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['type'])
# CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['type'])

# Redis connection with retry logic
def get_redis_client():
    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=1,  # DB diferente do auth service
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
throttler = Throttler(rate_limit=100, period=60)  # 100 requests per minute

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Data Service",
    description="Serviço de Dados Externos e Cache",
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
class StockData(BaseModel):
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    timestamp: datetime

class HistoricalData(BaseModel):
    symbol: str
    data: List[Dict[str, Any]]
    period: str
    timestamp: datetime

class MarketIndex(BaseModel):
    symbol: str
    name: str
    value: float
    change: float
    change_percent: float
    timestamp: datetime

# Utility functions
def get_cache_key(prefix: str, symbol: str, **kwargs) -> str:
    """Gerar chave de cache"""
    key_parts = [prefix, symbol.upper()]
    for k, v in kwargs.items():
        key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)

def cache_data(key: str, data: Any, ttl: int = 300):
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
            cache_hits.labels(level="l2", key_type="redis").inc()
            return json.loads(cached)
        else:
            cache_misses.labels(level="l2", key_type="redis").inc()
            return None
    except Exception as e:
        logger.error("Cache read failed", key=key, error=str(e))
        cache_misses.labels(level="l2", key_type="redis").inc()
        return None

async def fetch_yahoo_finance_data(symbol: str) -> Optional[Dict]:
    """Buscar dados do Yahoo Finance"""
    try:
        async with throttler:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            
            API_CALLS.labels(provider="yahoo_finance", status="success").inc()
            
            return {
                "symbol": symbol.upper(),
                "name": info.get('longName', symbol),
                "current_price": float(current_price),
                "previous_close": float(previous_close),
                "change": float(current_price - previous_close),
                "change_percent": float((current_price - previous_close) / previous_close * 100),
                "volume": int(hist['Volume'].iloc[-1]),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "dividend_yield": info.get('dividendYield'),
                "timestamp": datetime.utcnow()
            }
            
    except Exception as e:
        logger.error("Yahoo Finance API failed", symbol=symbol, error=str(e))
        API_CALLS.labels(provider="yahoo_finance", status="error").inc()
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
        
        # Verificar conectividade com Yahoo Finance
        test_ticker = yf.Ticker("AAPL")
        test_data = test_ticker.history(period="1d", timeout=5)
        
        return {
            "status": "healthy",
            "service": "data-service",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "redis": "healthy",
                "yahoo_finance": "healthy" if not test_data.empty else "degraded"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Métricas endpoint
@app.get("/metrics")
async def metrics():
    return generate_latest()

# Data endpoints
@app.get("/stock/{symbol}", response_model=StockData)
async def get_stock_data(symbol: str):
    """Obter dados de uma ação específica"""
    try:
        # Verificar cache primeiro
        cache_key = get_cache_key("stock", symbol)
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return StockData(**cached_data)
        
        # Buscar dados do Yahoo Finance
        data = await fetch_yahoo_finance_data(symbol)
        if not data:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        # Salvar no cache (5 minutos)
        cache_data(cache_key, data, ttl=300)
        
        return StockData(**data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get stock data failed", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch stock data")

@app.get("/stocks/batch")
async def get_multiple_stocks(symbols: str = Query(..., description="Comma-separated stock symbols")):
    """Obter dados de múltiplas ações"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        results = []
        
        for symbol in symbol_list:
            try:
                # Verificar cache
                cache_key = get_cache_key("stock", symbol)
                cached_data = get_cached_data(cache_key)
                
                if cached_data:
                    results.append(StockData(**cached_data))
                else:
                    # Buscar dados
                    data = await fetch_yahoo_finance_data(symbol)
                    if data:
                        cache_data(cache_key, data, ttl=300)
                        results.append(StockData(**data))
                        
            except Exception as e:
                logger.error("Failed to fetch stock", symbol=symbol, error=str(e))
                continue
        
        return {"stocks": results, "total": len(results)}
        
    except Exception as e:
        logger.error("Batch stock fetch failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch stocks")

@app.get("/stock/{symbol}/history", response_model=HistoricalData)
async def get_stock_history(
    symbol: str,
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
):
    """Obter dados históricos de uma ação"""
    try:
        # Verificar cache
        cache_key = get_cache_key("history", symbol, period=period)
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return HistoricalData(**cached_data)
        
        # Buscar dados históricos
        async with throttler:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")
            
            # Converter para formato JSON
            hist_data = []
            for date, row in hist.iterrows():
                hist_data.append({
                    "date": date.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            
            data = {
                "symbol": symbol.upper(),
                "data": hist_data,
                "period": period,
                "timestamp": datetime.utcnow()
            }
            
            # Cache por 1 hora para dados históricos
            cache_data(cache_key, data, ttl=3600)
            
            API_CALLS.labels(provider="yahoo_finance", status="success").inc()
            
            return HistoricalData(**data)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get stock history failed", symbol=symbol, error=str(e))
        API_CALLS.labels(provider="yahoo_finance", status="error").inc()
        raise HTTPException(status_code=500, detail="Failed to fetch historical data")

@app.get("/market/indices")
async def get_market_indices():
    """Obter dados dos principais índices de mercado"""
    try:
        indices = {
            "^BVSP": "Ibovespa",
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ"
        }
        
        results = []
        
        for symbol, name in indices.items():
            try:
                cache_key = get_cache_key("index", symbol)
                cached_data = get_cached_data(cache_key)
                
                if cached_data:
                    results.append(MarketIndex(**cached_data))
                else:
                    async with throttler:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="2d")
                        
                        if not hist.empty:
                            current_value = hist['Close'].iloc[-1]
                            previous_value = hist['Close'].iloc[-2] if len(hist) > 1 else current_value
                            
                            data = {
                                "symbol": symbol,
                                "name": name,
                                "value": float(current_value),
                                "change": float(current_value - previous_value),
                                "change_percent": float((current_value - previous_value) / previous_value * 100),
                                "timestamp": datetime.utcnow()
                            }
                            
                            cache_data(cache_key, data, ttl=300)
                            results.append(MarketIndex(**data))
                            
            except Exception as e:
                logger.error("Failed to fetch index", symbol=symbol, error=str(e))
                continue
        
        return {"indices": results, "total": len(results)}
        
    except Exception as e:
        logger.error("Get market indices failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch market indices")

@app.get("/search/{query}")
async def search_stocks(query: str):
    """Buscar ações por nome ou símbolo"""
    try:
        # Cache de busca
        cache_key = get_cache_key("search", query.lower())
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        # Busca simples - em produção, usar API de busca mais robusta
        # Por enquanto, retornar algumas ações brasileiras conhecidas
        brazilian_stocks = {
            "PETR4": "Petrobras",
            "VALE3": "Vale",
            "ITUB4": "Itaú Unibanco",
            "BBDC4": "Bradesco",
            "ABEV3": "Ambev",
            "WEGE3": "WEG",
            "MGLU3": "Magazine Luiza",
            "VVAR3": "Via Varejo",
            "JBSS3": "JBS",
            "SUZB3": "Suzano"
        }
        
        results = []
        query_lower = query.lower()
        
        for symbol, name in brazilian_stocks.items():
            if (query_lower in symbol.lower() or 
                query_lower in name.lower()):
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": "B3"
                })
        
        data = {"results": results, "query": query}
        cache_data(cache_key, data, ttl=3600)  # Cache por 1 hora
        
        return data
        
    except Exception as e:
        logger.error("Stock search failed", query=query, error=str(e))
        raise HTTPException(status_code=500, detail="Search failed")

@app.delete("/cache/{symbol}")
async def clear_cache(symbol: str):
    """Limpar cache de uma ação específica"""
    try:
        patterns = [
            get_cache_key("stock", symbol),
            get_cache_key("history", symbol, period="*"),
            get_cache_key("index", symbol)
        ]
        
        cleared = 0
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            if keys:
                cleared += redis_client.delete(*keys)
        
        return {"message": f"Cleared {cleared} cache entries for {symbol}"}
        
    except Exception as e:
        logger.error("Cache clear failed", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to clear cache")

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_config=None
    )

