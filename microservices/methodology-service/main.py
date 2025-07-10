"""
Serviço de Metodologias - Agente Investidor
Responsável por aplicar as 10 metodologias de investimento
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
from typing import List, Optional, Dict, Any
from datetime import datetime

# Adicionar path para importar módulos compartilhados
sys.path.append('/app')
sys.path.append('/app/microservices/shared')

from models.dto import (
    DadosFinanceiros, AnaliseResultado, MetodologiaInfo,
    AnaliseRequest, AnaliseResponse, ComparacaoRequest, ComparacaoResponse,
    RecomendacaoEnum
)

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
REQUEST_COUNT = Counter('methodology_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('methodology_request_duration_seconds', 'Request duration')
ANALYSIS_COUNT = Counter('methodology_analysis_total', 'Total analyses', ['methodology', 'recommendation'])
METHODOLOGY_USAGE = Counter('methodology_usage_total', 'Methodology usage', ['methodology'])

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=2,  # DB específico para metodologias
    decode_responses=True
)

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Methodology Service",
    description="Serviço de Metodologias de Investimento",
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

# Implementação das Metodologias (baseada no código existente)
class ValueInvesting:
    nome = "warren_buffett"
    descricao = (
        "Foco em empresas sólidas, vantagem competitiva (moat), "
        "gestão de qualidade, geração de caixa e compra com margem de segurança."
    )
    indicadores = ["P/E ratio", "ROE", "Debt/Equity", "Free Cash Flow", "Moat"]
    exemplos = ["Apple", "Coca-Cola", "Verisign", "GEICO", "BNSF Railway"]
    referencias = [
        "The Intelligent Investor",
        "Essays of Warren Buffett",
        "https://www.investopedia.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # P/E razoável
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 20
                pontos_fortes.append(f"P/E excelente: {dados.pe_ratio:.2f}")
            elif dados.pe_ratio < 25:
                score += 10
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")

        # ROE alto
        if dados.roe:
            if dados.roe > 15:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 10:
                score += 10
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Baixo endividamento: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 1.0:
                score += 8
                pontos_fortes.append(f"Endividamento moderado: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Alto endividamento: {dados.debt_to_equity:.2f}")

        # Margem de segurança (P/B baixo)
        if dados.pb_ratio:
            if dados.pb_ratio < 1.5:
                score += 15
                pontos_fortes.append(f"P/B atrativo: {dados.pb_ratio:.2f}")
            elif dados.pb_ratio < 3.0:
                score += 8
                pontos_fortes.append(f"P/B razoável: {dados.pb_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/B alto: {dados.pb_ratio:.2f}")

        # Dividendos consistentes
        if dados.dividend_yield:
            if dados.dividend_yield > 2:
                score += 10
                pontos_fortes.append(f"Bom dividend yield: {dados.dividend_yield:.2f}%")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="warren_buffett",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise baseada nos princípios de Warren Buffett"]
        )

class GrowthInvesting:
    nome = "growth_investing"
    descricao = "Foco em empresas com alto crescimento de receita e lucros"
    indicadores = ["Revenue Growth", "Earnings Growth", "PEG Ratio", "ROE"]
    exemplos = ["Amazon", "Tesla", "Netflix", "Google"]
    referencias = ["Common Stocks and Uncommon Profits", "Growth Stock Investing"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Crescimento de receita
        if dados.revenue_growth:
            if dados.revenue_growth > 20:
                score += 25
                pontos_fortes.append(f"Alto crescimento de receita: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 10:
                score += 15
                pontos_fortes.append(f"Bom crescimento de receita: {dados.revenue_growth:.2f}%")
            else:
                pontos_fracos.append(f"Baixo crescimento de receita: {dados.revenue_growth:.2f}%")

        # PEG Ratio
        if dados.peg_ratio:
            if dados.peg_ratio < 1:
                score += 20
                pontos_fortes.append(f"PEG atrativo: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 2:
                score += 10
                pontos_fortes.append(f"PEG razoável: {dados.peg_ratio:.2f}")
            else:
                pontos_fracos.append(f"PEG alto: {dados.peg_ratio:.2f}")

        # ROE para eficiência
        if dados.roe:
            if dados.roe > 20:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 15:
                score += 10
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")

        # Crescimento de lucros
        if dados.earnings_growth:
            if dados.earnings_growth > 25:
                score += 25
                pontos_fortes.append(f"Alto crescimento de lucros: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 15:
                score += 15
                pontos_fortes.append(f"Bom crescimento de lucros: {dados.earnings_growth:.2f}%")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="growth_investing",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise focada em crescimento"]
        )

class DividendInvesting:
    nome = "dividend_investing"
    descricao = "Foco em empresas que pagam dividendos consistentes e crescentes"
    indicadores = ["Dividend Yield", "Payout Ratio", "Dividend Growth", "Free Cash Flow"]
    exemplos = ["Johnson & Johnson", "Procter & Gamble", "Coca-Cola"]
    referencias = ["The Dividend Growth Investment Strategy"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Dividend Yield
        if dados.dividend_yield:
            if dados.dividend_yield > 4:
                score += 25
                pontos_fortes.append(f"Alto dividend yield: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 2:
                score += 15
                pontos_fortes.append(f"Bom dividend yield: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Baixo dividend yield: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")

        # Payout Ratio sustentável
        if dados.payout_ratio:
            if dados.payout_ratio < 60:
                score += 20
                pontos_fortes.append(f"Payout sustentável: {dados.payout_ratio:.2f}%")
            elif dados.payout_ratio < 80:
                score += 10
                pontos_fortes.append(f"Payout moderado: {dados.payout_ratio:.2f}%")
            else:
                pontos_fracos.append(f"Payout alto: {dados.payout_ratio:.2f}%")

        # Estabilidade financeira
        if dados.debt_to_equity and dados.debt_to_equity < 0.6:
            score += 15
            pontos_fortes.append("Baixo endividamento para sustentabilidade dos dividendos")

        # ROE para qualidade
        if dados.roe and dados.roe > 12:
            score += 15
            pontos_fortes.append(f"ROE sólido: {dados.roe:.2f}%")

        # P/E razoável
        if dados.pe_ratio and dados.pe_ratio < 20:
            score += 15
            pontos_fortes.append(f"P/E atrativo: {dados.pe_ratio:.2f}")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="dividend_investing",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise focada em dividendos"]
        )

# Dicionário de metodologias disponíveis
METODOLOGIAS = {
    "warren_buffett": ValueInvesting,
    "growth_investing": GrowthInvesting,
    "dividend_investing": DividendInvesting,
}

# Utility functions
def get_cache_key(prefix: str, symbol: str, metodologia: str = None) -> str:
    """Gerar chave de cache"""
    if metodologia:
        return f"{prefix}:{symbol}:{metodologia}"
    return f"{prefix}:{symbol}"

def cache_result(key: str, data: Any, ttl: int = 1800):
    """Salvar resultado no cache (30 minutos default)"""
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
            "service": "methodology-service",
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

# Methodology endpoints
@app.get("/methodologies", response_model=List[MetodologiaInfo])
async def list_methodologies():
    """Listar todas as metodologias disponíveis"""
    metodologias = []
    for nome, classe in METODOLOGIAS.items():
        metodologias.append(MetodologiaInfo(
            nome=classe.nome,
            descricao=classe.descricao,
            indicadores=classe.indicadores,
            exemplos=classe.exemplos,
            referencias=classe.referencias
        ))
    return metodologias

@app.get("/methodologies/{methodology_name}", response_model=MetodologiaInfo)
async def get_methodology_info(methodology_name: str):
    """Obter informações sobre uma metodologia específica"""
    if methodology_name not in METODOLOGIAS:
        raise HTTPException(status_code=404, detail="Methodology not found")
    
    classe = METODOLOGIAS[methodology_name]
    return MetodologiaInfo(
        nome=classe.nome,
        descricao=classe.descricao,
        indicadores=classe.indicadores,
        exemplos=classe.exemplos,
        referencias=classe.referencias
    )

@app.post("/analyze", response_model=AnaliseResponse)
async def analyze_stock(request: AnaliseRequest):
    """Analisar uma ação usando metodologias especificadas"""
    try:
        # Buscar dados financeiros se não fornecidos
        if not request.dados_financeiros:
            dados = await fetch_financial_data(request.symbol)
            if not dados:
                raise HTTPException(status_code=404, detail=f"Financial data not found for {request.symbol}")
        else:
            dados = request.dados_financeiros

        # Determinar metodologias a usar
        metodologias_usar = request.metodologias or list(METODOLOGIAS.keys())
        
        resultados = []
        for metodologia_nome in metodologias_usar:
            if metodologia_nome not in METODOLOGIAS:
                continue
                
            # Verificar cache
            cache_key = get_cache_key("analysis", request.symbol, metodologia_nome)
            cached_result = get_cached_result(cache_key)
            
            if cached_result:
                resultados.append(AnaliseResultado(**cached_result))
                continue
            
            # Executar análise
            metodologia_classe = METODOLOGIAS[metodologia_nome]
            resultado = metodologia_classe.analisar(dados)
            
            # Salvar no cache
            cache_result(cache_key, resultado.dict())
            
            # Métricas
            METHODOLOGY_USAGE.labels(methodology=metodologia_nome).inc()
            ANALYSIS_COUNT.labels(
                methodology=metodologia_nome,
                recommendation=resultado.recomendacao.value
            ).inc()
            
            resultados.append(resultado)

        # Criar resumo
        if resultados:
            scores = [r.score for r in resultados]
            recomendacoes = [r.recomendacao.value for r in resultados]
            
            resumo = {
                "score_medio": sum(scores) / len(scores),
                "score_maximo": max(scores),
                "score_minimo": min(scores),
                "total_metodologias": len(resultados),
                "recomendacao_predominante": max(set(recomendacoes), key=recomendacoes.count)
            }
        else:
            resumo = {}

        return AnaliseResponse(
            symbol=request.symbol,
            resultados=resultados,
            resumo=resumo
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Analysis failed", symbol=request.symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/compare", response_model=ComparacaoResponse)
async def compare_stocks(request: ComparacaoRequest):
    """Comparar múltiplas ações usando uma metodologia"""
    try:
        if request.metodologia not in METODOLOGIAS:
            raise HTTPException(status_code=404, detail="Methodology not found")
        
        metodologia_classe = METODOLOGIAS[request.metodologia]
        resultados = []
        
        for symbol in request.symbols:
            # Buscar dados financeiros
            dados = await fetch_financial_data(symbol)
            if not dados:
                continue
                
            # Verificar cache
            cache_key = get_cache_key("analysis", symbol, request.metodologia)
            cached_result = get_cached_result(cache_key)
            
            if cached_result:
                resultados.append(AnaliseResultado(**cached_result))
            else:
                # Executar análise
                resultado = metodologia_classe.analisar(dados)
                cache_result(cache_key, resultado.dict())
                resultados.append(resultado)

        # Criar ranking
        ranking = []
        for resultado in sorted(resultados, key=lambda x: x.score, reverse=True):
            ranking.append({
                "symbol": resultado.symbol,
                "score": resultado.score,
                "recomendacao": resultado.recomendacao.value,
                "posicao": len(ranking) + 1
            })

        return ComparacaoResponse(
            metodologia=request.metodologia,
            resultados=resultados,
            ranking=ranking
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Comparison failed", error=str(e))
        raise HTTPException(status_code=500, detail="Comparison failed")

@app.delete("/cache/{symbol}")
async def clear_cache(symbol: str, methodology: Optional[str] = None):
    """Limpar cache de análises"""
    try:
        if methodology:
            key = get_cache_key("analysis", symbol, methodology)
            cleared = redis_client.delete(key)
        else:
            pattern = get_cache_key("analysis", symbol, "*")
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
        port=8003,
        reload=True,
        log_config=None
    )



class DefensiveValue:
    nome = "benjamin_graham"
    descricao = (
        "Foco em segurança do principal, análise fundamentalista, "
        "margem de segurança, empresas com dívida controlada."
    )
    indicadores = ["P/E ratio", "P/B ratio", "Debt/Equity", "Current Ratio", "Dividend Yield"]
    exemplos = ["GEICO"]
    referencias = ["Security Analysis", "The Intelligent Investor"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # P/E < 15
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 25
                pontos_fortes.append(f"P/E dentro do critério Graham: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E acima do critério Graham: {dados.pe_ratio:.2f}")

        # P/B < 1.5
        if dados.pb_ratio:
            if dados.pb_ratio < 1.5:
                score += 20
                pontos_fortes.append(f"P/B excelente: {dados.pb_ratio:.2f}")
            elif dados.pb_ratio < 2.5:
                score += 10
                pontos_fortes.append(f"P/B razoável: {dados.pb_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/B alto: {dados.pb_ratio:.2f}")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.3:
                score += 20
                pontos_fortes.append(f"Baixíssimo endividamento: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.6:
                score += 10
                pontos_fortes.append(f"Endividamento controlado: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Alto endividamento: {dados.debt_to_equity:.2f}")

        # Current Ratio > 2
        if dados.current_ratio:
            if dados.current_ratio > 2:
                score += 15
                pontos_fortes.append(f"Excelente liquidez corrente: {dados.current_ratio:.2f}")
            elif dados.current_ratio > 1.5:
                score += 8
                pontos_fortes.append(f"Boa liquidez corrente: {dados.current_ratio:.2f}")

        # Dividend Yield
        if dados.dividend_yield and dados.dividend_yield > 2:
            score += 10
            pontos_fortes.append(f"Paga dividendos: {dados.dividend_yield:.2f}%")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="benjamin_graham",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise baseada nos critérios de Benjamin Graham"]
        )

class GrowthAtReasonablePrice:
    nome = "peter_lynch"
    descricao = "Crescimento a preço razoável - PEG ratio baixo com crescimento sustentável"
    indicadores = ["PEG Ratio", "Revenue Growth", "Earnings Growth", "P/E Ratio"]
    exemplos = ["Fidelity Magellan Fund holdings"]
    referencias = ["One Up On Wall Street", "Beating the Street"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # PEG Ratio é o principal critério
        if dados.peg_ratio:
            if dados.peg_ratio < 0.5:
                score += 30
                pontos_fortes.append(f"PEG excelente: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1.0:
                score += 20
                pontos_fortes.append(f"PEG bom: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1.5:
                score += 10
                pontos_fortes.append(f"PEG razoável: {dados.peg_ratio:.2f}")
            else:
                pontos_fracos.append(f"PEG alto: {dados.peg_ratio:.2f}")

        # Crescimento de receita
        if dados.revenue_growth:
            if dados.revenue_growth > 15:
                score += 20
                pontos_fortes.append(f"Alto crescimento de receita: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 8:
                score += 10
                pontos_fortes.append(f"Bom crescimento de receita: {dados.revenue_growth:.2f}%")

        # P/E razoável
        if dados.pe_ratio:
            if dados.pe_ratio < 20:
                score += 15
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")
            elif dados.pe_ratio > 30:
                pontos_fracos.append(f"P/E muito alto: {dados.pe_ratio:.2f}")

        # ROE para qualidade
        if dados.roe and dados.roe > 15:
            score += 15
            pontos_fortes.append(f"ROE sólido: {dados.roe:.2f}%")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="peter_lynch",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise GARP - Growth at Reasonable Price"]
        )

class TechnicalTrading:
    nome = "linda_bradford_raschke"
    descricao = "Trading baseado em análise técnica, momentum e padrões de preço"
    indicadores = ["RSI", "Moving Averages", "Volume", "Volatility"]
    exemplos = ["Day trading", "Swing trading"]
    referencias = ["Street Smarts", "Trading Sardines"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Volatilidade para oportunidades de trading
        if dados.volatility:
            if 15 <= dados.volatility <= 35:
                score += 25
                pontos_fortes.append(f"Volatilidade ideal para trading: {dados.volatility:.2f}%")
            elif dados.volatility > 50:
                pontos_fracos.append(f"Volatilidade muito alta: {dados.volatility:.2f}%")
            elif dados.volatility < 10:
                pontos_fracos.append(f"Volatilidade muito baixa: {dados.volatility:.2f}%")

        # Volume alto indica interesse
        if dados.volume and dados.volume > 1000000:
            score += 20
            pontos_fortes.append("Alto volume de negociação")

        # Momentum (aproximado via mudança de preço)
        if dados.change_percent:
            if abs(dados.change_percent) > 2:
                score += 15
                pontos_fortes.append(f"Movimento significativo: {dados.change_percent:.2f}%")

        # Beta para correlação com mercado
        if dados.beta:
            if 0.8 <= dados.beta <= 1.5:
                score += 15
                pontos_fortes.append(f"Beta adequado: {dados.beta:.2f}")

        # Market cap adequado para liquidez
        if dados.market_cap and dados.market_cap > 1000000000:  # > 1B
            score += 15
            pontos_fortes.append("Boa liquidez (large cap)")

        # Determinar recomendação baseada em momentum
        if score >= 60:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 30:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="linda_bradford_raschke",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise técnica para trading de curto prazo"]
        )

class PassiveInvesting:
    nome = "john_bogle"
    descricao = "Investimento passivo em índices de baixo custo"
    indicadores = ["Expense Ratio", "Tracking Error", "Diversification"]
    exemplos = ["Vanguard Index Funds", "ETFs"]
    referencias = ["The Little Book of Common Sense Investing"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 50  # Score base para estratégia passiva
        pontos_fortes = []
        pontos_fracos = []

        # Para investimento passivo, preferimos empresas estáveis
        # Market cap grande
        if dados.market_cap and dados.market_cap > 10000000000:  # > 10B
            score += 20
            pontos_fortes.append("Large cap - adequado para investimento passivo")

        # Beta próximo de 1 (acompanha o mercado)
        if dados.beta:
            if 0.8 <= dados.beta <= 1.2:
                score += 15
                pontos_fortes.append(f"Beta próximo ao mercado: {dados.beta:.2f}")

        # Dividend yield para renda passiva
        if dados.dividend_yield:
            if dados.dividend_yield > 2:
                score += 10
                pontos_fortes.append(f"Dividendos para renda passiva: {dados.dividend_yield:.2f}%")

        # Baixa volatilidade
        if dados.volatility:
            if dados.volatility < 25:
                score += 10
                pontos_fortes.append(f"Baixa volatilidade: {dados.volatility:.2f}%")

        # ROE consistente
        if dados.roe and dados.roe > 10:
            score += 5
            pontos_fortes.append(f"ROE consistente: {dados.roe:.2f}%")

        # Sempre recomendação neutra para estratégia passiva
        recomendacao = RecomendacaoEnum.NEUTRO

        return AnaliseResultado(
            metodologia="john_bogle",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise para estratégia de investimento passivo"]
        )

class MacroTrading:
    nome = "george_soros"
    descricao = "Trading baseado em tendências macroeconômicas globais"
    indicadores = ["Currency Exposure", "Economic Indicators", "Global Trends"]
    exemplos = ["Quantum Fund trades"]
    referencias = ["The Alchemy of Finance"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Para macro trading, focamos em empresas sensíveis a ciclos econômicos
        # Beta alto indica sensibilidade ao mercado
        if dados.beta:
            if dados.beta > 1.2:
                score += 20
                pontos_fortes.append(f"Alta sensibilidade ao mercado: {dados.beta:.2f}")
            elif dados.beta < 0.8:
                pontos_fracos.append(f"Baixa sensibilidade ao mercado: {dados.beta:.2f}")

        # Volatilidade alta para oportunidades macro
        if dados.volatility:
            if dados.volatility > 30:
                score += 20
                pontos_fortes.append(f"Alta volatilidade para macro trading: {dados.volatility:.2f}%")

        # Market cap grande para liquidez
        if dados.market_cap and dados.market_cap > 5000000000:  # > 5B
            score += 15
            pontos_fortes.append("Boa liquidez para posições grandes")

        # Setores sensíveis a macro
        if dados.sector:
            macro_sensitive_sectors = ["Financials", "Energy", "Materials", "Technology"]
            if dados.sector in macro_sensitive_sectors:
                score += 15
                pontos_fortes.append(f"Setor sensível a macro: {dados.sector}")

        # Volume alto
        if dados.volume and dados.volume > 5000000:
            score += 10
            pontos_fortes.append("Alto volume para execução de grandes posições")

        # Determinar recomendação
        if score >= 60:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 30:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="george_soros",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise para macro trading baseada em tendências globais"]
        )

class ActivistInvesting:
    nome = "carl_icahn"
    descricao = "Investimento ativista para influenciar mudanças corporativas"
    indicadores = ["Undervaluation", "Management Issues", "Asset Value"]
    exemplos = ["Corporate restructuring targets"]
    referencias = ["Activist investing strategies"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Subvalorização (P/B baixo)
        if dados.pb_ratio:
            if dados.pb_ratio < 1.0:
                score += 25
                pontos_fortes.append(f"Potencialmente subvalorizada: P/B {dados.pb_ratio:.2f}")
            elif dados.pb_ratio < 1.5:
                score += 15
                pontos_fortes.append(f"P/B atrativo: {dados.pb_ratio:.2f}")

        # ROE baixo indica ineficiência de gestão
        if dados.roe:
            if dados.roe < 10:
                score += 20
                pontos_fortes.append(f"ROE baixo - oportunidade de melhoria: {dados.roe:.2f}%")

        # Market cap adequado para influência
        if dados.market_cap:
            if 1000000000 <= dados.market_cap <= 50000000000:  # 1B - 50B
                score += 15
                pontos_fortes.append("Tamanho adequado para ativismo")

        # Debt/Equity alto pode indicar problemas de gestão
        if dados.debt_to_equity:
            if dados.debt_to_equity > 0.8:
                score += 15
                pontos_fortes.append(f"Alto endividamento - oportunidade de reestruturação: {dados.debt_to_equity:.2f}")

        # P/E baixo indica subvalorização
        if dados.pe_ratio:
            if dados.pe_ratio < 12:
                score += 15
                pontos_fortes.append(f"P/E baixo: {dados.pe_ratio:.2f}")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="carl_icahn",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise para investimento ativista"]
        )

class IncomeInvesting:
    nome = "income_investing"
    descricao = "Foco em geração de renda através de dividendos e juros"
    indicadores = ["Dividend Yield", "Payout Ratio", "Dividend Growth", "Stability"]
    exemplos = ["REITs", "Utilities", "Dividend aristocrats"]
    referencias = ["Income investing strategies"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Dividend yield alto
        if dados.dividend_yield:
            if dados.dividend_yield > 5:
                score += 30
                pontos_fortes.append(f"Alto dividend yield: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 3:
                score += 20
                pontos_fortes.append(f"Bom dividend yield: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 1:
                score += 10
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Baixo dividend yield: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")

        # Payout ratio sustentável
        if dados.payout_ratio:
            if dados.payout_ratio < 70:
                score += 20
                pontos_fortes.append(f"Payout sustentável: {dados.payout_ratio:.2f}%")
            elif dados.payout_ratio < 90:
                score += 10
                pontos_fortes.append(f"Payout moderado: {dados.payout_ratio:.2f}%")
            else:
                pontos_fracos.append(f"Payout muito alto: {dados.payout_ratio:.2f}%")

        # Estabilidade (baixa volatilidade)
        if dados.volatility:
            if dados.volatility < 20:
                score += 15
                pontos_fortes.append(f"Baixa volatilidade: {dados.volatility:.2f}%")

        # Debt/Equity controlado
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.6:
                score += 10
                pontos_fortes.append("Endividamento controlado")

        # ROE para sustentabilidade
        if dados.roe and dados.roe > 8:
            score += 5
            pontos_fortes.append(f"ROE adequado: {dados.roe:.2f}%")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="income_investing",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise focada em geração de renda"]
        )

class AggressiveGrowth:
    nome = "aggressive_growth"
    descricao = "Crescimento agressivo com foco em empresas disruptivas"
    indicadores = ["Revenue Growth", "Market Disruption", "Innovation", "Scalability"]
    exemplos = ["Startups", "Tech companies", "Disruptive businesses"]
    referencias = ["Growth investing strategies"]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Crescimento de receita muito alto
        if dados.revenue_growth:
            if dados.revenue_growth > 50:
                score += 35
                pontos_fortes.append(f"Crescimento explosivo: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 30:
                score += 25
                pontos_fortes.append(f"Alto crescimento: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 15:
                score += 15
                pontos_fortes.append(f"Bom crescimento: {dados.revenue_growth:.2f}%")

        # Setor de tecnologia/inovação
        if dados.sector:
            growth_sectors = ["Technology", "Healthcare", "Communication Services"]
            if dados.sector in growth_sectors:
                score += 20
                pontos_fortes.append(f"Setor de crescimento: {dados.sector}")

        # Market cap menor para potencial de crescimento
        if dados.market_cap:
            if dados.market_cap < 2000000000:  # < 2B (small/mid cap)
                score += 15
                pontos_fortes.append("Small/Mid cap com potencial de crescimento")

        # Alta volatilidade é aceitável para growth
        if dados.volatility:
            if dados.volatility > 40:
                score += 10
                pontos_fortes.append("Alta volatilidade típica de growth stocks")

        # ROE alto indica eficiência
        if dados.roe and dados.roe > 20:
            score += 10
            pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")

        # Determinar recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            metodologia="aggressive_growth",
            symbol=dados.symbol,
            score=min(score, 100),
            recomendacao=recomendacao,
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            observacoes=["Análise para crescimento agressivo"]
        )

# Dicionário de metodologias disponíveis - ATUALIZADO COM TODAS AS 10
METODOLOGIAS = {
    "warren_buffett": ValueInvesting,
    "benjamin_graham": DefensiveValue,
    "peter_lynch": GrowthAtReasonablePrice,
    "growth_investing": GrowthInvesting,
    "dividend_investing": DividendInvesting,
    "linda_bradford_raschke": TechnicalTrading,
    "john_bogle": PassiveInvesting,
    "george_soros": MacroTrading,
    "carl_icahn": ActivistInvesting,
    "income_investing": IncomeInvesting,
    "aggressive_growth": AggressiveGrowth,
}


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
            methodologies = message.get('methodologies', [])
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
            
            # Executar análises
            resultados = []
            metodologias_usar = methodologies if methodologies else list(METODOLOGIAS.keys())
            
            for metodologia_nome in metodologias_usar:
                if metodologia_nome not in METODOLOGIAS:
                    continue
                
                metodologia_classe = METODOLOGIAS[metodologia_nome]
                resultado = metodologia_classe.analisar(dados)
                resultados.append(resultado.dict())
                
                # Métricas
                METHODOLOGY_USAGE.labels(methodology=metodologia_nome).inc()
                ANALYSIS_COUNT.labels(
                    methodology=metodologia_nome,
                    recommendation=resultado.recomendacao.value
                ).inc()
            
            # Criar resumo
            if resultados:
                scores = [r['score'] for r in resultados]
                recomendacoes = [r['recomendacao'] for r in resultados]
                
                resumo = {
                    "score_medio": sum(scores) / len(scores),
                    "score_maximo": max(scores),
                    "score_minimo": min(scores),
                    "total_metodologias": len(resultados),
                    "recomendacao_predominante": max(set(recomendacoes), key=recomendacoes.count)
                }
            else:
                resumo = {}
            
            # Enviar resultado
            success_message = MessageSchemas.analysis_completed(
                request_id=request_id,
                symbol=symbol,
                results={
                    "resultados": resultados,
                    "resumo": resumo,
                    "user_id": user_id
                }
            )
            
            send_message(Topics.METHODOLOGY_ANALYSIS_COMPLETED, success_message, key=symbol)
            logger.info("Async analysis completed", symbol=symbol, request_id=request_id)
            
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
        topics=[Topics.METHODOLOGY_ANALYSIS_REQUESTED],
        group_id="methodology-service-group",
        message_handler=handle_analysis_request,
        auto_offset_reset='latest'
    )

# Endpoint para análise assíncrona
@app.post("/analyze/async")
async def analyze_stock_async(request: AnaliseRequest, user_id: str = Query(...)):
    """Solicitar análise assíncrona via Kafka"""
    try:
        request_id = f"req_{datetime.utcnow().timestamp()}_{user_id}"
        
        # Enviar mensagem para Kafka
        message = MessageSchemas.analysis_requested(
            user_id=user_id,
            symbol=request.symbol,
            methodologies=request.metodologias
        )
        message['request_id'] = request_id
        
        success = send_message(Topics.METHODOLOGY_ANALYSIS_REQUESTED, message, key=request.symbol)
        
        if success:
            return {
                "message": "Analysis request submitted",
                "request_id": request_id,
                "symbol": request.symbol,
                "status": "processing"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit analysis request")
            
    except Exception as e:
        logger.error("Failed to submit async analysis", symbol=request.symbol, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit analysis request")

# Inicializar consumer Kafka em startup
@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização"""
    logger.info("Starting Methodology Service")
    
    # Iniciar consumer Kafka em thread separada
    consumer_thread = threading.Thread(target=start_kafka_consumer, daemon=True)
    consumer_thread.start()
    
    logger.info("Kafka consumer started")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de encerramento"""
    logger.info("Shutting down Methodology Service")
    kafka_client.close()

