"""
Serviço de Análises Financeiras - Agente Investidor
Responsável por calcular indicadores fundamentalistas e análises técnicas
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import start_http_server
import structlog
import time
import redis
import json
import httpx
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Adicionar path para importar módulos compartilhados
sys.path.append('/app')
sys.path.append('/app/microservices/shared')

from models.dto import DadosFinanceiros

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
REQUEST_COUNT = Counter('analysis_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('analysis_request_duration_seconds', 'Request duration')
ANALYSIS_COUNT = Counter('analysis_calculations_total', 'Total analyses', ['type'])
INDICATOR_USAGE = Counter('indicator_usage_total', 'Indicator usage', ['indicator'])

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=3,  # DB específico para análises
    decode_responses=True
)

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Analysis Service",
    description="Serviço de Análises Financeiras e Indicadores",
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

# DTOs específicos do serviço
class IndicadorFundamentalista(BaseModel):
    nome: str
    valor: float
    interpretacao: str
    categoria: str  # "rentabilidade", "liquidez", "endividamento", "eficiencia"

class AnaliseIndicadores(BaseModel):
    symbol: str
    indicadores: List[IndicadorFundamentalista]
    score_geral: float
    resumo: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnaliseComparativa(BaseModel):
    symbols: List[str]
    indicador: str
    valores: Dict[str, float]
    ranking: List[Dict[str, Any]]
    media_setor: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnaliseSetorial(BaseModel):
    setor: str
    symbols: List[str]
    indicadores_medios: Dict[str, float]
    melhores_empresas: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnaliseRisco(BaseModel):
    symbol: str
    volatilidade: float
    beta: float
    var_95: float  # Value at Risk 95%
    sharpe_ratio: Optional[float] = None
    classificacao_risco: str  # "Baixo", "Moderado", "Alto"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnaliseValuation(BaseModel):
    symbol: str
    preco_atual: float
    preco_justo_dcf: Optional[float] = None
    preco_justo_multiplos: Optional[float] = None
    margem_seguranca: Optional[float] = None
    recomendacao: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Calculadora de Indicadores Fundamentalistas
class CalculadoraIndicadores:
    
    @staticmethod
    def calcular_todos_indicadores(dados: DadosFinanceiros) -> List[IndicadorFundamentalista]:
        """Calcular todos os indicadores fundamentalistas"""
        indicadores = []
        
        # Indicadores de Rentabilidade
        if dados.roe:
            interpretacao = CalculadoraIndicadores._interpretar_roe(dados.roe)
            indicadores.append(IndicadorFundamentalista(
                nome="ROE",
                valor=dados.roe,
                interpretacao=interpretacao,
                categoria="rentabilidade"
            ))
        
        if dados.roa:
            interpretacao = CalculadoraIndicadores._interpretar_roa(dados.roa)
            indicadores.append(IndicadorFundamentalista(
                nome="ROA",
                valor=dados.roa,
                interpretacao=interpretacao,
                categoria="rentabilidade"
            ))
        
        if dados.roic:
            interpretacao = CalculadoraIndicadores._interpretar_roic(dados.roic)
            indicadores.append(IndicadorFundamentalista(
                nome="ROIC",
                valor=dados.roic,
                interpretacao=interpretacao,
                categoria="rentabilidade"
            ))
        
        # Indicadores de Valuation
        if dados.pe_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_pe(dados.pe_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="P/E",
                valor=dados.pe_ratio,
                interpretacao=interpretacao,
                categoria="valuation"
            ))
        
        if dados.pb_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_pb(dados.pb_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="P/B",
                valor=dados.pb_ratio,
                interpretacao=interpretacao,
                categoria="valuation"
            ))
        
        if dados.ps_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_ps(dados.ps_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="P/S",
                valor=dados.ps_ratio,
                interpretacao=interpretacao,
                categoria="valuation"
            ))
        
        if dados.ev_ebitda:
            interpretacao = CalculadoraIndicadores._interpretar_ev_ebitda(dados.ev_ebitda)
            indicadores.append(IndicadorFundamentalista(
                nome="EV/EBITDA",
                valor=dados.ev_ebitda,
                interpretacao=interpretacao,
                categoria="valuation"
            ))
        
        if dados.peg_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_peg(dados.peg_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="PEG",
                valor=dados.peg_ratio,
                interpretacao=interpretacao,
                categoria="valuation"
            ))
        
        # Indicadores de Endividamento
        if dados.debt_to_equity:
            interpretacao = CalculadoraIndicadores._interpretar_debt_equity(dados.debt_to_equity)
            indicadores.append(IndicadorFundamentalista(
                nome="Debt/Equity",
                valor=dados.debt_to_equity,
                interpretacao=interpretacao,
                categoria="endividamento"
            ))
        
        # Indicadores de Liquidez
        if dados.current_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_current_ratio(dados.current_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="Current Ratio",
                valor=dados.current_ratio,
                interpretacao=interpretacao,
                categoria="liquidez"
            ))
        
        if dados.quick_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_quick_ratio(dados.quick_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="Quick Ratio",
                valor=dados.quick_ratio,
                interpretacao=interpretacao,
                categoria="liquidez"
            ))
        
        # Indicadores de Dividendos
        if dados.dividend_yield:
            interpretacao = CalculadoraIndicadores._interpretar_dividend_yield(dados.dividend_yield)
            indicadores.append(IndicadorFundamentalista(
                nome="Dividend Yield",
                valor=dados.dividend_yield,
                interpretacao=interpretacao,
                categoria="dividendos"
            ))
        
        if dados.payout_ratio:
            interpretacao = CalculadoraIndicadores._interpretar_payout_ratio(dados.payout_ratio)
            indicadores.append(IndicadorFundamentalista(
                nome="Payout Ratio",
                valor=dados.payout_ratio,
                interpretacao=interpretacao,
                categoria="dividendos"
            ))
        
        return indicadores
    
    @staticmethod
    def _interpretar_roe(roe: float) -> str:
        if roe > 20:
            return "Excelente - ROE muito alto indica alta rentabilidade"
        elif roe > 15:
            return "Bom - ROE acima da média do mercado"
        elif roe > 10:
            return "Razoável - ROE dentro da média"
        else:
            return "Baixo - ROE abaixo da média, pode indicar ineficiência"
    
    @staticmethod
    def _interpretar_roa(roa: float) -> str:
        if roa > 10:
            return "Excelente - Empresa muito eficiente no uso dos ativos"
        elif roa > 5:
            return "Bom - Boa eficiência no uso dos ativos"
        elif roa > 2:
            return "Razoável - Eficiência moderada"
        else:
            return "Baixo - Baixa eficiência no uso dos ativos"
    
    @staticmethod
    def _interpretar_roic(roic: float) -> str:
        if roic > 15:
            return "Excelente - Muito eficiente na geração de valor"
        elif roic > 10:
            return "Bom - Boa geração de valor sobre o capital investido"
        elif roic > 5:
            return "Razoável - Geração de valor moderada"
        else:
            return "Baixo - Baixa geração de valor"
    
    @staticmethod
    def _interpretar_pe(pe: float) -> str:
        if pe < 10:
            return "Muito baixo - Pode indicar subvalorização ou problemas"
        elif pe < 15:
            return "Baixo - Potencialmente atrativo"
        elif pe < 25:
            return "Razoável - Dentro da média do mercado"
        elif pe < 35:
            return "Alto - Expectativas de crescimento elevadas"
        else:
            return "Muito alto - Pode indicar sobrevalorização"
    
    @staticmethod
    def _interpretar_pb(pb: float) -> str:
        if pb < 1:
            return "Muito baixo - Negociando abaixo do valor patrimonial"
        elif pb < 1.5:
            return "Baixo - Potencialmente atrativo"
        elif pb < 3:
            return "Razoável - Dentro da média"
        else:
            return "Alto - Pode indicar sobrevalorização"
    
    @staticmethod
    def _interpretar_ps(ps: float) -> str:
        if ps < 1:
            return "Muito baixo - Potencialmente subvalorizada"
        elif ps < 2:
            return "Baixo - Atrativo em relação à receita"
        elif ps < 5:
            return "Razoável - Múltiplo moderado"
        else:
            return "Alto - Múltiplo elevado em relação à receita"
    
    @staticmethod
    def _interpretar_ev_ebitda(ev_ebitda: float) -> str:
        if ev_ebitda < 8:
            return "Baixo - Potencialmente atrativo"
        elif ev_ebitda < 12:
            return "Razoável - Múltiplo moderado"
        elif ev_ebitda < 20:
            return "Alto - Múltiplo elevado"
        else:
            return "Muito alto - Pode indicar sobrevalorização"
    
    @staticmethod
    def _interpretar_peg(peg: float) -> str:
        if peg < 0.5:
            return "Excelente - Crescimento a preço muito atrativo"
        elif peg < 1:
            return "Bom - Crescimento a preço razoável"
        elif peg < 1.5:
            return "Razoável - Crescimento a preço justo"
        else:
            return "Alto - Crescimento caro"
    
    @staticmethod
    def _interpretar_debt_equity(debt_equity: float) -> str:
        if debt_equity < 0.3:
            return "Baixo - Endividamento muito controlado"
        elif debt_equity < 0.6:
            return "Moderado - Endividamento razoável"
        elif debt_equity < 1:
            return "Alto - Endividamento elevado mas controlado"
        else:
            return "Muito alto - Endividamento preocupante"
    
    @staticmethod
    def _interpretar_current_ratio(current_ratio: float) -> str:
        if current_ratio > 2:
            return "Excelente - Muito boa liquidez corrente"
        elif current_ratio > 1.5:
            return "Bom - Boa liquidez corrente"
        elif current_ratio > 1:
            return "Razoável - Liquidez adequada"
        else:
            return "Baixo - Liquidez insuficiente"
    
    @staticmethod
    def _interpretar_quick_ratio(quick_ratio: float) -> str:
        if quick_ratio > 1.5:
            return "Excelente - Muito boa liquidez imediata"
        elif quick_ratio > 1:
            return "Bom - Boa liquidez imediata"
        elif quick_ratio > 0.8:
            return "Razoável - Liquidez adequada"
        else:
            return "Baixo - Liquidez imediata insuficiente"
    
    @staticmethod
    def _interpretar_dividend_yield(dividend_yield: float) -> str:
        if dividend_yield > 6:
            return "Muito alto - Excelente para renda, verificar sustentabilidade"
        elif dividend_yield > 4:
            return "Alto - Bom para geração de renda"
        elif dividend_yield > 2:
            return "Moderado - Dividendos razoáveis"
        else:
            return "Baixo - Foco em crescimento, não em renda"
    
    @staticmethod
    def _interpretar_payout_ratio(payout_ratio: float) -> str:
        if payout_ratio < 30:
            return "Baixo - Empresa retém a maioria dos lucros"
        elif payout_ratio < 60:
            return "Moderado - Equilíbrio entre distribuição e retenção"
        elif payout_ratio < 80:
            return "Alto - Distribui a maior parte dos lucros"
        else:
            return "Muito alto - Pode comprometer crescimento futuro"

# Calculadora de Análise de Risco
class CalculadoraRisco:
    
    @staticmethod
    def calcular_analise_risco(dados: DadosFinanceiros, precos_historicos: List[float] = None) -> AnaliseRisco:
        """Calcular análise de risco completa"""
        
        # Volatilidade
        volatilidade = dados.volatility or 0
        
        # Beta
        beta = dados.beta or 1.0
        
        # VaR 95% (aproximação simples)
        var_95 = CalculadoraRisco._calcular_var(precos_historicos) if precos_historicos else volatilidade * 1.65
        
        # Sharpe Ratio (aproximação)
        sharpe_ratio = CalculadoraRisco._calcular_sharpe_ratio(dados, precos_historicos)
        
        # Classificação de risco
        classificacao = CalculadoraRisco._classificar_risco(volatilidade, beta)
        
        return AnaliseRisco(
            symbol=dados.symbol,
            volatilidade=volatilidade,
            beta=beta,
            var_95=var_95,
            sharpe_ratio=sharpe_ratio,
            classificacao_risco=classificacao
        )
    
    @staticmethod
    def _calcular_var(precos: List[float], confianca: float = 0.95) -> float:
        """Calcular Value at Risk"""
        if not precos or len(precos) < 2:
            return 0
        
        returns = []
        for i in range(1, len(precos)):
            ret = (precos[i] - precos[i-1]) / precos[i-1]
            returns.append(ret)
        
        returns_array = np.array(returns)
        return np.percentile(returns_array, (1 - confianca) * 100) * 100
    
    @staticmethod
    def _calcular_sharpe_ratio(dados: DadosFinanceiros, precos: List[float] = None) -> Optional[float]:
        """Calcular Sharpe Ratio aproximado"""
        if not precos or len(precos) < 2:
            return None
        
        returns = []
        for i in range(1, len(precos)):
            ret = (precos[i] - precos[i-1]) / precos[i-1]
            returns.append(ret)
        
        if not returns:
            return None
        
        returns_array = np.array(returns)
        excess_return = np.mean(returns_array) - 0.02/252  # Assumindo 2% risk-free anual
        volatility = np.std(returns_array)
        
        if volatility == 0:
            return None
        
        return (excess_return / volatility) * np.sqrt(252)  # Anualizado
    
    @staticmethod
    def _classificar_risco(volatilidade: float, beta: float) -> str:
        """Classificar nível de risco"""
        score_vol = 0
        score_beta = 0
        
        # Score baseado na volatilidade
        if volatilidade < 15:
            score_vol = 1
        elif volatilidade < 25:
            score_vol = 2
        else:
            score_vol = 3
        
        # Score baseado no beta
        if beta < 0.8:
            score_beta = 1
        elif beta < 1.2:
            score_beta = 2
        else:
            score_beta = 3
        
        score_total = (score_vol + score_beta) / 2
        
        if score_total <= 1.5:
            return "Baixo"
        elif score_total <= 2.5:
            return "Moderado"
        else:
            return "Alto"

# Utility functions
def get_cache_key(prefix: str, symbol: str, extra: str = None) -> str:
    """Gerar chave de cache"""
    if extra:
        return f"{prefix}:{symbol}:{extra}"
    return f"{prefix}:{symbol}"

def cache_result(key: str, data: Any, ttl: int = 3600):
    """Salvar resultado no cache (1 hora default)"""
    try:
        redis_client.setex(key, ttl, json.dumps(data, default=str))
    except Exception as e:
        logger.error("Cache save failed", key=key, error=str(e))

def get_cached_result(key: str) -> Optional[Any]:
    """Recuperar resultado do cache"""
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error("Cache read failed", key=key, error=str(e))
        return None

async def fetch_financial_data(symbol: str) -> Optional[DadosFinanceiros]:
    """Buscar dados financeiros do Data Service"""
    try:
        data_service_url = os.getenv("DATA_SERVICE_URL", "http://data-service:8002")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{data_service_url}/stock/{symbol}")
            if response.status_code == 200:
                data = response.json()
                return DadosFinanceiros(**data)
            return None
    except Exception as e:
        logger.error("Failed to fetch financial data", symbol=symbol, error=str(e))
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
        redis_client.ping()
        return {
            "status": "healthy",
            "service": "analysis-service",
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

# Analysis endpoints
@app.get("/indicators/{symbol}", response_model=AnaliseIndicadores)
async def analyze_indicators(symbol: str):
    """Analisar todos os indicadores fundamentalistas de uma ação"""
    try:
        # Verificar cache
        cache_key = get_cache_key("indicators", symbol)
        cached_result = get_cached_result(cache_key)
        
        if cached_result:
            return AnaliseIndicadores(**cached_result)
        
        # Buscar dados financeiros
        dados = await fetch_financial_data(symbol)
        if not dados:
            raise HTTPException(status_code=404, detail=f"Financial data not found for {symbol}")
        
        # Calcular indicadores
        indicadores = CalculadoraIndicadores.calcular_todos_indicadores(dados)
        
        # Calcular score geral
        if indicadores:
            scores = []
            for ind in indicadores:
                # Score baseado na interpretação (simplificado)
                if "Excelente" in ind.interpretacao:
                    scores.append(90)
                elif "Bom" in ind.interpretacao:
                    scores.append(75)
                elif "Razoável" in ind.interpretacao:
                    scores.append(60)
                elif "Alto" in ind.interpretacao and ind.categoria == "valuation":
                    scores.append(40)
                else:
                    scores.append(50)
            
            score_geral = sum(scores) / len(scores)
        else:
            score_geral = 0
        
        # Criar resumo
        if score_geral >= 80:
            resumo = "Empresa com indicadores fundamentalistas excelentes"
        elif score_geral >= 70:
            resumo = "Empresa com bons indicadores fundamentalistas"
        elif score_geral >= 60:
            resumo = "Empresa com indicadores fundamentalistas razoáveis"
        else:
            resumo = "Empresa com indicadores fundamentalistas fracos"
        
        resultado = AnaliseIndicadores(
            symbol=symbol,
            indicadores=indicadores,
            score_geral=score_geral,
            resumo=resumo
        )
        
        # Salvar no cache
        cache_result(cache_key, resultado.dict())
        
        # Métricas
        ANALYSIS_COUNT.labels(type="indicators").inc()
        for ind in indicadores:
            INDICATOR_USAGE.labels(indicator=ind.nome).inc()
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Indicators analysis failed", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/risk/{symbol}", response_model=AnaliseRisco)
async def analyze_risk(symbol: str):
    """Analisar risco de uma ação"""
    try:
        # Verificar cache
        cache_key = get_cache_key("risk", symbol)
        cached_result = get_cached_result(cache_key)
        
        if cached_result:
            return AnaliseRisco(**cached_result)
        
        # Buscar dados financeiros
        dados = await fetch_financial_data(symbol)
        if not dados:
            raise HTTPException(status_code=404, detail=f"Financial data not found for {symbol}")
        
        # Calcular análise de risco
        resultado = CalculadoraRisco.calcular_analise_risco(dados)
        
        # Salvar no cache
        cache_result(cache_key, resultado.dict())
        
        # Métricas
        ANALYSIS_COUNT.labels(type="risk").inc()
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Risk analysis failed", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Risk analysis failed")

@app.post("/compare", response_model=AnaliseComparativa)
async def compare_stocks(symbols: List[str], indicador: str):
    """Comparar múltiplas ações por um indicador específico"""
    try:
        valores = {}
        
        for symbol in symbols:
            dados = await fetch_financial_data(symbol)
            if not dados:
                continue
            
            # Extrair valor do indicador
            valor = getattr(dados, indicador.lower().replace('/', '_').replace(' ', '_'), None)
            if valor is not None:
                valores[symbol] = valor
        
        if not valores:
            raise HTTPException(status_code=404, detail="No data found for comparison")
        
        # Criar ranking
        ranking = []
        for symbol, valor in sorted(valores.items(), key=lambda x: x[1], reverse=True):
            ranking.append({
                "symbol": symbol,
                "valor": valor,
                "posicao": len(ranking) + 1
            })
        
        # Calcular média
        media_setor = sum(valores.values()) / len(valores)
        
        resultado = AnaliseComparativa(
            symbols=list(valores.keys()),
            indicador=indicador,
            valores=valores,
            ranking=ranking,
            media_setor=media_setor
        )
        
        # Métricas
        ANALYSIS_COUNT.labels(type="comparison").inc()
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Comparison failed", error=str(e))
        raise HTTPException(status_code=500, detail="Comparison failed")

@app.delete("/cache/{symbol}")
async def clear_cache(symbol: str, analysis_type: Optional[str] = None):
    """Limpar cache de análises"""
    try:
        if analysis_type:
            key = get_cache_key(analysis_type, symbol)
            cleared = redis_client.delete(key)
        else:
            pattern = f"*:{symbol}:*"
            keys = redis_client.keys(pattern)
            cleared = redis_client.delete(*keys) if keys else 0
        
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
        port=8004,
        reload=True,
        log_config=None
    )


# Integração com Kafka
sys.path.append('/app/microservices/shared')
from messaging import Topics, MessageSchemas, send_message, consume_messages
import threading

# Consumer para processar análises assíncronas
def start_kafka_consumer():
    """Iniciar consumer Kafka em thread separada"""
    def handle_analysis_request(topic: str, message: Dict[str, Any]):
        """Processar requisição de análise assíncrona"""
        try:
            logger.info("Processing async analysis request", message=message)
            
            request_id = message.get('request_id')
            symbol = message.get('symbol')
            analysis_type = message.get('analysis_type', 'indicators')
            user_id = message.get('user_id')
            
            if not symbol:
                logger.error("Missing symbol in analysis request", message=message)
                return
            
            # Buscar dados financeiros
            dados = asyncio.run(fetch_financial_data(symbol))
            if not dados:
                # Enviar evento de falha
                failure_message = {
                    "request_id": request_id,
                    "symbol": symbol,
                    "error": "Financial data not found",
                    "user_id": user_id
                }
                send_message(Topics.ANALYSIS_FAILED, failure_message, key=symbol)
                return
            
            # Executar análise baseada no tipo
            resultado = None
            
            if analysis_type == 'indicators':
                # Calcular indicadores
                indicadores = CalculadoraIndicadores.calcular_todos_indicadores(dados)
                
                # Calcular score geral
                if indicadores:
                    scores = []
                    for ind in indicadores:
                        if "Excelente" in ind.interpretacao:
                            scores.append(90)
                        elif "Bom" in ind.interpretacao:
                            scores.append(75)
                        elif "Razoável" in ind.interpretacao:
                            scores.append(60)
                        elif "Alto" in ind.interpretacao and ind.categoria == "valuation":
                            scores.append(40)
                        else:
                            scores.append(50)
                    
                    score_geral = sum(scores) / len(scores)
                else:
                    score_geral = 0
                
                # Criar resumo
                if score_geral >= 80:
                    resumo = "Empresa com indicadores fundamentalistas excelentes"
                elif score_geral >= 70:
                    resumo = "Empresa com bons indicadores fundamentalistas"
                elif score_geral >= 60:
                    resumo = "Empresa com indicadores fundamentalistas razoáveis"
                else:
                    resumo = "Empresa com indicadores fundamentalistas fracos"
                
                resultado = {
                    "type": "indicators",
                    "symbol": symbol,
                    "indicadores": [ind.dict() for ind in indicadores],
                    "score_geral": score_geral,
                    "resumo": resumo
                }
                
            elif analysis_type == 'risk':
                # Calcular análise de risco
                analise_risco = CalculadoraRisco.calcular_analise_risco(dados)
                resultado = {
                    "type": "risk",
                    "symbol": symbol,
                    **analise_risco.dict()
                }
            
            if resultado:
                # Enviar resultado
                success_message = MessageSchemas.analysis_completed(
                    request_id=request_id,
                    symbol=symbol,
                    results={
                        **resultado,
                        "user_id": user_id
                    }
                )
                
                send_message(Topics.ANALYSIS_COMPLETED, success_message, key=symbol)
                logger.info("Async analysis completed", symbol=symbol, request_id=request_id)
                
                # Métricas
                ANALYSIS_COUNT.labels(type=analysis_type).inc()
            
        except Exception as e:
            logger.error("Error processing async analysis", error=str(e), message=message)
            
            # Enviar evento de falha
            failure_message = {
                "request_id": message.get('request_id'),
                "symbol": message.get('symbol'),
                "error": str(e),
                "user_id": message.get('user_id')
            }
            send_message(Topics.ANALYSIS_FAILED, failure_message, key=message.get('symbol'))
    
    # Iniciar consumer
    consume_messages(
        topics=[Topics.ANALYSIS_REQUESTED],
        group_id="analysis-service-group",
        message_handler=handle_analysis_request,
        auto_offset_reset='latest'
    )

# Endpoint para análise assíncrona
@app.post("/analyze/async")
async def analyze_async(symbol: str, analysis_type: str = "indicators", user_id: str = Query(...)):
    """Solicitar análise assíncrona via Kafka"""
    try:
        request_id = f"req_{datetime.utcnow().timestamp()}_{user_id}"
        
        # Enviar mensagem para Kafka
        message = {
            "event_type": "analysis_requested",
            "request_id": request_id,
            "user_id": user_id,
            "symbol": symbol,
            "analysis_type": analysis_type
        }
        
        success = send_message(Topics.ANALYSIS_REQUESTED, message, key=symbol)
        
        if success:
            return {
                "message": "Analysis request submitted",
                "request_id": request_id,
                "symbol": symbol,
                "analysis_type": analysis_type,
                "status": "processing"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit analysis request")
            
    except Exception as e:
        logger.error("Failed to submit async analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit analysis request")

# Inicializar consumer Kafka em startup
@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização"""
    logger.info("Starting Analysis Service")
    
    # Iniciar consumer Kafka em thread separada
    consumer_thread = threading.Thread(target=start_kafka_consumer, daemon=True)
    consumer_thread.start()
    
    logger.info("Kafka consumer started")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de encerramento"""
    logger.info("Shutting down Analysis Service")
    kafka_client.close()


# Integração com comunicação entre serviços
sys.path.append('/app/microservices/shared')
try:
    from communication import service_client, validate_user_token, get_stock_data, analyze_stock
    logger.info("Comunicação entre serviços configurada")
except ImportError as e:
    logger.warning(f"Erro ao importar comunicação: {e}")
    service_client = None

# Middleware para autenticação
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware para validar autenticação em endpoints protegidos"""
    
    # Endpoints que não precisam de autenticação
    public_endpoints = ["/health", "/metrics", "/docs", "/openapi.json"]
    
    if request.url.path in public_endpoints:
        return await call_next(request)
    
    # Verificar token de autorização
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Token de autorização necessário"}
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Validar token com serviço de autenticação
        if service_client:
            validation_result = await validate_user_token(token)
            if not validation_result.get("valid"):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token inválido"}
                )
            
            # Adicionar informações do usuário ao request
            request.state.user_id = validation_result.get("user_id")
            request.state.user_email = validation_result.get("email")
        
    except Exception as e:
        logger.error(f"Erro na validação do token: {e}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Erro na validação do token"}
        )
    
    return await call_next(request)

# Endpoint para análise completa integrada
@app.post("/analyze/complete")
async def analyze_complete(request: CompleteAnalysisRequest):
    """Análise completa integrada com múltiplas metodologias"""
    try:
        # Obter dados da ação via serviço de dados
        if service_client:
            stock_data = await get_stock_data(request.symbol)
        else:
            stock_data = {"symbol": request.symbol}  # Fallback
        
        results = []
        
        # Analisar com múltiplas metodologias
        for methodology in request.methodologies:
            try:
                if service_client:
                    result = await analyze_stock(request.symbol, methodology, stock_data)
                    results.append(result)
                else:
                    # Fallback local
                    results.append({
                        "methodology": methodology,
                        "score": 50,
                        "recommendation": "NEUTRO",
                        "message": "Análise local - dados limitados"
                    })
            except Exception as e:
                logger.warning(f"Erro na análise com {methodology}: {e}")
                results.append({
                    "methodology": methodology,
                    "error": str(e)
                })
        
        # Calcular score médio
        valid_scores = [r.get("score", 0) for r in results if "score" in r]
        average_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        # Determinar recomendação geral
        if average_score >= 70:
            overall_recommendation = "COMPRA"
        elif average_score >= 40:
            overall_recommendation = "NEUTRO"
        else:
            overall_recommendation = "VENDA"
        
        complete_analysis = {
            "symbol": request.symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": round(average_score, 2),
            "overall_recommendation": overall_recommendation,
            "methodologies_analyzed": len(request.methodologies),
            "successful_analyses": len(valid_scores),
            "detailed_results": results,
            "stock_data": stock_data
        }
        
        # Publicar resultado no Kafka
        if kafka_producer:
            await kafka_producer.send_complete_analysis(complete_analysis)
        
        return complete_analysis
        
    except Exception as e:
        logger.error(f"Erro na análise completa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para health check de todos os serviços
@app.get("/health/services")
async def health_check_services():
    """Verifica saúde de todos os serviços conectados"""
    if not service_client:
        return {"error": "Cliente de serviços não disponível"}
    
    try:
        health_status = await service_client.health_check_all()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": health_status
        }
    except Exception as e:
        logger.error(f"Erro no health check dos serviços: {e}")
        return {"error": str(e)}

