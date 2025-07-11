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

from shared.models.dto import (
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
ANALYSIS_COUNT = Counter('methodology_analysis_total', 'Total analysis', ['methodology'])

# Configurações
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:8002")

# Conexão Redis
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Conectado ao Redis com sucesso")
except Exception as e:
    logger.error(f"Erro ao conectar ao Redis: {e}")
    redis_client = None

# FastAPI app
app = FastAPI(
    title="Methodology Service",
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

# Implementação das 10 Metodologias

class ValueInvesting:
    nome = "warren_buffett"
    descricao = "Foco em empresas sólidas, vantagem competitiva (moat), gestão de qualidade, geração de caixa e compra com margem de segurança."
    indicadores = ["P/E ratio", "ROE", "Debt/Equity", "Free Cash Flow", "Moat"]
    
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
            if dados.debt_to_equity < 0.3:
                score += 15
                pontos_fortes.append(f"Dívida muito baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.5:
                score += 10
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

        # Margem de lucro
        if dados.profit_margin:
            if dados.profit_margin > 15:
                score += 15
                pontos_fortes.append(f"Margem excelente: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 10:
                score += 10
                pontos_fortes.append(f"Margem boa: {dados.profit_margin:.2f}%")
            else:
                pontos_fracos.append(f"Margem baixa: {dados.profit_margin:.2f}%")

        # Crescimento consistente
        if dados.earnings_growth:
            if dados.earnings_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento forte: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 5:
                score += 10
                pontos_fortes.append(f"Crescimento moderado: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento baixo: {dados.earnings_growth:.2f}%")

        # Free Cash Flow
        if dados.free_cash_flow and dados.free_cash_flow > 0:
            score += 15
            pontos_fortes.append("Free Cash Flow positivo")
        elif dados.free_cash_flow:
            pontos_fracos.append("Free Cash Flow negativo")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Warren Buffett - Value Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada nos critérios de Buffett: empresas com vantagem competitiva, boa gestão e preço razoável."
        )

class DefensiveValue:
    nome = "benjamin_graham"
    descricao = "Estratégia conservadora focando em empresas subvalorizadas com fundamentos sólidos e baixo risco."
    indicadores = ["P/B ratio", "Current Ratio", "Debt/Equity", "Dividend Yield", "P/E"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # P/B baixo
        if dados.price_to_book:
            if dados.price_to_book < 1.0:
                score += 25
                pontos_fortes.append(f"P/B excelente: {dados.price_to_book:.2f}")
            elif dados.price_to_book < 1.5:
                score += 15
                pontos_fortes.append(f"P/B bom: {dados.price_to_book:.2f}")
            else:
                pontos_fracos.append(f"P/B alto: {dados.price_to_book:.2f}")

        # Current Ratio
        if dados.current_ratio:
            if dados.current_ratio > 2.0:
                score += 20
                pontos_fortes.append(f"Liquidez excelente: {dados.current_ratio:.2f}")
            elif dados.current_ratio > 1.5:
                score += 15
                pontos_fortes.append(f"Liquidez boa: {dados.current_ratio:.2f}")
            else:
                pontos_fracos.append(f"Liquidez baixa: {dados.current_ratio:.2f}")

        # Dividend Yield
        if dados.dividend_yield:
            if dados.dividend_yield > 4:
                score += 20
                pontos_fortes.append(f"Dividend yield alto: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 2:
                score += 10
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")

        # P/E conservador
        if dados.pe_ratio:
            if dados.pe_ratio < 12:
                score += 15
                pontos_fortes.append(f"P/E conservador: {dados.pe_ratio:.2f}")
            elif dados.pe_ratio < 18:
                score += 10
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")

        # Dívida baixa
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.3:
                score += 20
                pontos_fortes.append(f"Dívida muito baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.5:
                score += 10
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Benjamin Graham - Defensive Value",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Estratégia conservadora focando em empresas subvalorizadas com fundamentos sólidos."
        )

class GrowthAtReasonablePrice:
    nome = "peter_lynch"
    descricao = "Busca empresas com crescimento sólido a preços razoáveis, focando no PEG ratio."
    indicadores = ["PEG ratio", "Earnings Growth", "P/E", "ROE", "Revenue Growth"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # PEG ratio
        if dados.peg_ratio:
            if dados.peg_ratio < 1.0:
                score += 30
                pontos_fortes.append(f"PEG excelente: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1.5:
                score += 20
                pontos_fortes.append(f"PEG bom: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 2.0:
                score += 10
                pontos_fortes.append(f"PEG aceitável: {dados.peg_ratio:.2f}")
            else:
                pontos_fracos.append(f"PEG alto: {dados.peg_ratio:.2f}")

        # Crescimento de lucros
        if dados.earnings_growth:
            if dados.earnings_growth > 20:
                score += 25
                pontos_fortes.append(f"Crescimento excelente: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 15:
                score += 20
                pontos_fortes.append(f"Crescimento forte: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento bom: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento baixo: {dados.earnings_growth:.2f}%")

        # ROE
        if dados.roe:
            if dados.roe > 20:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 15:
                score += 15
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # Revenue Growth
        if dados.revenue_growth:
            if dados.revenue_growth > 15:
                score += 15
                pontos_fortes.append(f"Crescimento receita forte: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 10:
                score += 10
                pontos_fortes.append(f"Crescimento receita bom: {dados.revenue_growth:.2f}%")

        # P/E razoável para crescimento
        if dados.pe_ratio and dados.earnings_growth:
            if dados.pe_ratio < dados.earnings_growth:
                score += 10
                pontos_fortes.append("P/E menor que crescimento")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Peter Lynch - Growth at Reasonable Price",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Busca empresas com crescimento sólido a preços razoáveis, focando no PEG ratio."
        )

class DividendInvesting:
    nome = "dividend_investing"
    descricao = "Foco em empresas que pagam dividendos consistentes e crescentes."
    indicadores = ["Dividend Yield", "Payout Ratio", "Dividend Growth", "Free Cash Flow"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Dividend Yield
        if dados.dividend_yield:
            if dados.dividend_yield > 6:
                score += 25
                pontos_fortes.append(f"Dividend yield alto: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 4:
                score += 20
                pontos_fortes.append(f"Dividend yield bom: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 2:
                score += 15
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Dividend yield baixo: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")

        # Payout Ratio
        if dados.payout_ratio:
            if 30 <= dados.payout_ratio <= 60:
                score += 20
                pontos_fortes.append(f"Payout ratio ideal: {dados.payout_ratio:.2f}%")
            elif dados.payout_ratio < 80:
                score += 10
                pontos_fortes.append(f"Payout ratio aceitável: {dados.payout_ratio:.2f}%")
            else:
                pontos_fracos.append(f"Payout ratio alto: {dados.payout_ratio:.2f}%")

        # Free Cash Flow
        if dados.free_cash_flow and dados.free_cash_flow > 0:
            score += 20
            pontos_fortes.append("Free Cash Flow positivo")
        elif dados.free_cash_flow:
            pontos_fracos.append("Free Cash Flow negativo")

        # Estabilidade (ROE)
        if dados.roe and dados.roe > 12:
            score += 15
            pontos_fortes.append(f"ROE estável: {dados.roe:.2f}%")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 20
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Dividend Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Foco em empresas que pagam dividendos consistentes e crescentes."
        )

class GrowthInvesting:
    nome = "growth_investing"
    descricao = "Foco em empresas com alto potencial de crescimento, mesmo a preços premium."
    indicadores = ["Revenue Growth", "Earnings Growth", "ROE", "Profit Margin"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Revenue Growth
        if dados.revenue_growth:
            if dados.revenue_growth > 25:
                score += 30
                pontos_fortes.append(f"Crescimento receita excelente: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 15:
                score += 20
                pontos_fortes.append(f"Crescimento receita forte: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 10:
                score += 10
                pontos_fortes.append(f"Crescimento receita bom: {dados.revenue_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento receita baixo: {dados.revenue_growth:.2f}%")

        # Earnings Growth
        if dados.earnings_growth:
            if dados.earnings_growth > 25:
                score += 30
                pontos_fortes.append(f"Crescimento lucros excelente: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 15:
                score += 20
                pontos_fortes.append(f"Crescimento lucros forte: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 10:
                score += 10
                pontos_fortes.append(f"Crescimento lucros bom: {dados.earnings_growth:.2f}%")

        # ROE alto
        if dados.roe:
            if dados.roe > 25:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 20:
                score += 15
                pontos_fortes.append(f"ROE muito bom: {dados.roe:.2f}%")
            elif dados.roe > 15:
                score += 10
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")

        # Profit Margin
        if dados.profit_margin:
            if dados.profit_margin > 20:
                score += 20
                pontos_fortes.append(f"Margem excelente: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 15:
                score += 15
                pontos_fortes.append(f"Margem muito boa: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 10:
                score += 10
                pontos_fortes.append(f"Margem boa: {dados.profit_margin:.2f}%")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Growth Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Foco em empresas com alto potencial de crescimento."
        )

# Dicionário de metodologias
METODOLOGIAS = {
    "warren_buffett": ValueInvesting,
    "benjamin_graham": DefensiveValue,
    "peter_lynch": GrowthAtReasonablePrice,
    "dividend_investing": DividendInvesting,
    "growth_investing": GrowthInvesting,
    "carl_icahn": ActivistInvesting,
    "income_investing": IncomeInvesting,
    "passive_investing": PassiveInvesting,
    "technical_trading": TechnicalTrading,
    "macro_trading": MacroTrading,
}

# Integração com Kafka
sys.path.append('/app/microservices/shared')
try:
    from shared.messaging.kafka_client import KafkaProducer
    kafka_producer = KafkaProducer()
    logger.info("Kafka producer inicializado")
except Exception as e:
    logger.warning(f"Kafka não disponível: {e}")
    kafka_producer = None

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

# Endpoints

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "methodology-service",
        "timestamp": datetime.utcnow().isoformat(),
        "redis_connected": redis_client is not None,
        "kafka_connected": kafka_producer is not None
    }

@app.get("/metrics")
async def get_metrics():
    return generate_latest()

@app.get("/metodologias", response_model=List[MetodologiaInfo])
async def listar_metodologias():
    """Lista todas as metodologias disponíveis"""
    metodologias = []
    for nome, classe in METODOLOGIAS.items():
        metodologias.append(MetodologiaInfo(
            nome=nome,
            descricao=classe.descricao,
            indicadores=classe.indicadores
        ))
    return metodologias

@app.post("/analisar", response_model=AnaliseResponse)
async def analisar_acao(request: AnaliseRequest):
    """Analisa uma ação usando metodologia específica"""
    try:
        # Verificar se metodologia existe
        if request.metodologia not in METODOLOGIAS:
            raise HTTPException(
                status_code=400,
                detail=f"Metodologia '{request.metodologia}' não encontrada"
            )

        # Buscar dados da ação
        dados = await buscar_dados_acao(request.symbol)
        
        # Aplicar metodologia
        metodologia_classe = METODOLOGIAS[request.metodologia]
        resultado = metodologia_classe.analisar(dados)
        
        # Incrementar métrica
        ANALYSIS_COUNT.labels(methodology=request.metodologia).inc()
        
        # Cache do resultado
        if redis_client:
            cache_key = f"analysis:{request.symbol}:{request.metodologia}"
            cache_data = {
                "resultado": resultado.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            redis_client.setex(cache_key, 3600, json.dumps(cache_data))  # 1 hora
        
        # Publicar evento no Kafka
        if kafka_producer:
            event = {
                "type": "analysis_completed",
                "symbol": request.symbol,
                "methodology": request.metodologia,
                "score": resultado.score,
                "recommendation": resultado.recomendacao.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            await kafka_producer.send("analysis-events", event)
        
        return AnaliseResponse(
            symbol=request.symbol,
            metodologia=request.metodologia,
            resultado=resultado,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/comparar", response_model=ComparacaoResponse)
async def comparar_metodologias(request: ComparacaoRequest):
    """Compara múltiplas metodologias para uma ação"""
    try:
        # Buscar dados da ação
        dados = await buscar_dados_acao(request.symbol)
        
        resultados = {}
        for metodologia in request.metodologias:
            if metodologia in METODOLOGIAS:
                metodologia_classe = METODOLOGIAS[metodologia]
                resultado = metodologia_classe.analisar(dados)
                resultados[metodologia] = resultado
                
                # Incrementar métrica
                ANALYSIS_COUNT.labels(methodology=metodologia).inc()
        
        # Encontrar melhor metodologia
        melhor_metodologia = max(resultados.keys(), 
                               key=lambda k: resultados[k].score)
        
        return ComparacaoResponse(
            symbol=request.symbol,
            resultados=resultados,
            melhor_metodologia=melhor_metodologia,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Erro na comparação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def buscar_dados_acao(symbol: str) -> DadosFinanceiros:
    """Busca dados da ação no serviço de dados"""
    try:
        # Verificar cache primeiro
        if redis_client:
            cache_key = f"stock_data:{symbol}"
            cached_data = redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return DadosFinanceiros(**data)
        
        # Buscar no serviço de dados
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATA_SERVICE_URL}/stock/{symbol}")
            response.raise_for_status()
            data = response.json()
            
            # Cache por 30 minutos
            if redis_client:
                redis_client.setex(cache_key, 1800, json.dumps(data))
            
            return DadosFinanceiros(**data)
            
    except Exception as e:
        logger.error(f"Erro ao buscar dados para {symbol}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Dados não encontrados para {symbol}"
        )

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    start_http_server(8000)
    
    # Iniciar aplicação
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_config=None  # Usar nosso logging estruturado
    )

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
from shared.messaging import Topics, MessageSchemas, send_message, consume_messages
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


class ActivistInvesting:
    nome = "carl_icahn"
    descricao = "Investimento ativista, busca por mudanças em empresas, foco em governança, eficiência e destravamento de valor."
    indicadores = ["Governança", "Potencial de Reestruturação", "Participação Acionária", "ROE"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # ROE como indicador de eficiência
        if dados.roe:
            if dados.roe > 20:
                score += 25
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 15:
                score += 15
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # Margem de lucro baixa indica potencial de melhoria
        if dados.profit_margin:
            if dados.profit_margin < 10:
                score += 20
                pontos_fortes.append(f"Margem baixa com potencial: {dados.profit_margin:.2f}%")
            elif dados.profit_margin < 15:
                score += 10
                pontos_fortes.append(f"Margem moderada: {dados.profit_margin:.2f}%")

        # Dívida alta pode indicar necessidade de reestruturação
        if dados.debt_to_equity:
            if dados.debt_to_equity > 1.0:
                score += 15
                pontos_fortes.append(f"Alta alavancagem para reestruturação: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity > 0.5:
                score += 10
                pontos_fortes.append(f"Alavancagem moderada: {dados.debt_to_equity:.2f}")

        # P/B baixo indica subvalorização
        if dados.price_to_book:
            if dados.price_to_book < 1.0:
                score += 20
                pontos_fortes.append(f"P/B baixo - subvalorizada: {dados.price_to_book:.2f}")
            elif dados.price_to_book < 1.5:
                score += 15
                pontos_fortes.append(f"P/B atrativo: {dados.price_to_book:.2f}")

        # Free Cash Flow negativo pode indicar ineficiência
        if dados.free_cash_flow and dados.free_cash_flow < 0:
            score += 20
            pontos_fortes.append("FCF negativo - potencial de melhoria")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Carl Icahn - Activist Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Busca empresas com potencial de reestruturação e melhoria de governança."
        )

class IncomeInvesting:
    nome = "income_investing"
    descricao = "Foco em geração de renda consistente através de dividendos e juros."
    indicadores = ["Dividend Yield", "Payout Ratio", "Dividend Growth", "Stability"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Dividend Yield alto
        if dados.dividend_yield:
            if dados.dividend_yield > 5:
                score += 30
                pontos_fortes.append(f"Dividend yield alto: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 3:
                score += 20
                pontos_fortes.append(f"Dividend yield bom: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 1:
                score += 10
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Dividend yield baixo: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")

        # Payout Ratio sustentável
        if dados.payout_ratio:
            if 40 <= dados.payout_ratio <= 70:
                score += 25
                pontos_fortes.append(f"Payout ratio sustentável: {dados.payout_ratio:.2f}%")
            elif dados.payout_ratio < 80:
                score += 15
                pontos_fortes.append(f"Payout ratio aceitável: {dados.payout_ratio:.2f}%")
            else:
                pontos_fracos.append(f"Payout ratio alto: {dados.payout_ratio:.2f}%")

        # Estabilidade financeira
        if dados.current_ratio:
            if dados.current_ratio > 1.5:
                score += 20
                pontos_fortes.append(f"Liquidez boa: {dados.current_ratio:.2f}")
            elif dados.current_ratio > 1.0:
                score += 10
                pontos_fortes.append(f"Liquidez adequada: {dados.current_ratio:.2f}")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Dívida baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 1.0:
                score += 10
                pontos_fortes.append(f"Dívida moderada: {dados.debt_to_equity:.2f}")

        # ROE estável
        if dados.roe and dados.roe > 10:
            score += 10
            pontos_fortes.append(f"ROE estável: {dados.roe:.2f}%")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Income Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Foco em geração de renda consistente através de dividendos."
        )

class PassiveInvesting:
    nome = "passive_investing"
    descricao = "Estratégia de investimento passivo em índices e ETFs diversificados."
    indicadores = ["Diversification", "Low Fees", "Market Beta", "Tracking Error"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Beta próximo de 1 (acompanha mercado)
        if dados.beta:
            if 0.8 <= dados.beta <= 1.2:
                score += 30
                pontos_fortes.append(f"Beta próximo ao mercado: {dados.beta:.2f}")
            elif 0.6 <= dados.beta <= 1.4:
                score += 20
                pontos_fortes.append(f"Beta moderado: {dados.beta:.2f}")
            else:
                pontos_fracos.append(f"Beta muito volátil: {dados.beta:.2f}")

        # P/E próximo à média do mercado
        if dados.pe_ratio:
            if 12 <= dados.pe_ratio <= 20:
                score += 25
                pontos_fortes.append(f"P/E próximo à média: {dados.pe_ratio:.2f}")
            elif 8 <= dados.pe_ratio <= 25:
                score += 15
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")

        # ROE consistente
        if dados.roe:
            if 10 <= dados.roe <= 20:
                score += 20
                pontos_fortes.append(f"ROE consistente: {dados.roe:.2f}%")
            elif dados.roe > 8:
                score += 10
                pontos_fortes.append(f"ROE adequado: {dados.roe:.2f}%")

        # Dividend Yield moderado
        if dados.dividend_yield:
            if 1 <= dados.dividend_yield <= 4:
                score += 15
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.6:
                score += 10
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Passive Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Estratégia de investimento passivo em índices diversificados."
        )

class TechnicalTrading:
    nome = "technical_trading"
    descricao = "Análise técnica baseada em padrões de preço e volume."
    indicadores = ["RSI", "MACD", "Volume", "Moving Averages", "Support/Resistance"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Simulação de indicadores técnicos baseados em dados fundamentais
        
        # Volume (usando market cap como proxy)
        if dados.market_cap:
            if dados.market_cap > 10000000000:  # > 10B
                score += 20
                pontos_fortes.append("Alta liquidez - market cap grande")
            elif dados.market_cap > 1000000000:  # > 1B
                score += 15
                pontos_fortes.append("Liquidez adequada")

        # Volatilidade (usando beta)
        if dados.beta:
            if 0.8 <= dados.beta <= 1.5:
                score += 25
                pontos_fortes.append(f"Volatilidade adequada para trading: {dados.beta:.2f}")
            elif dados.beta > 1.5:
                score += 15
                pontos_fortes.append(f"Alta volatilidade: {dados.beta:.2f}")
            else:
                pontos_fracos.append(f"Baixa volatilidade: {dados.beta:.2f}")

        # Momentum (usando earnings growth)
        if dados.earnings_growth:
            if dados.earnings_growth > 15:
                score += 20
                pontos_fortes.append(f"Momentum positivo: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 5:
                score += 10
                pontos_fortes.append(f"Momentum moderado: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Momentum fraco: {dados.earnings_growth:.2f}%")

        # Tendência (usando P/E como proxy de sentimento)
        if dados.pe_ratio:
            if 15 <= dados.pe_ratio <= 25:
                score += 15
                pontos_fortes.append("Sentimento equilibrado")
            elif dados.pe_ratio > 25:
                score += 10
                pontos_fortes.append("Sentimento otimista")

        # Free Cash Flow como suporte
        if dados.free_cash_flow and dados.free_cash_flow > 0:
            score += 20
            pontos_fortes.append("Suporte fundamental sólido")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Technical Trading",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise técnica baseada em padrões de preço e volume."
        )

class MacroTrading:
    nome = "macro_trading"
    descricao = "Investimento baseado em tendências macroeconômicas globais."
    indicadores = ["Economic Cycles", "Interest Rates", "Currency", "Commodities", "Sector Rotation"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Sensibilidade a juros (usando debt/equity)
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.3:
                score += 25
                pontos_fortes.append(f"Baixa sensibilidade a juros: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.6:
                score += 15
                pontos_fortes.append(f"Sensibilidade moderada a juros: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Alta sensibilidade a juros: {dados.debt_to_equity:.2f}")

        # Exposição internacional (usando market cap como proxy)
        if dados.market_cap:
            if dados.market_cap > 50000000000:  # > 50B
                score += 20
                pontos_fortes.append("Exposição global - multinacional")
            elif dados.market_cap > 10000000000:  # > 10B
                score += 15
                pontos_fortes.append("Exposição regional")

        # Resistência a ciclos (usando ROE)
        if dados.roe:
            if dados.roe > 15:
                score += 20
                pontos_fortes.append(f"Resistente a ciclos: ROE {dados.roe:.2f}%")
            elif dados.roe > 10:
                score += 10
                pontos_fortes.append(f"Moderadamente cíclico: ROE {dados.roe:.2f}%")

        # Margem de segurança em cenários adversos
        if dados.current_ratio:
            if dados.current_ratio > 2.0:
                score += 15
                pontos_fortes.append(f"Margem de segurança alta: {dados.current_ratio:.2f}")
            elif dados.current_ratio > 1.5:
                score += 10
                pontos_fortes.append(f"Margem de segurança adequada: {dados.current_ratio:.2f}")

        # Pricing power (usando profit margin)
        if dados.profit_margin:
            if dados.profit_margin > 15:
                score += 20
                pontos_fortes.append(f"Alto pricing power: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 10:
                score += 10
                pontos_fortes.append(f"Pricing power moderado: {dados.profit_margin:.2f}%")

        # Recomendação
        if score >= 70:
            recomendacao = RecomendacaoEnum.COMPRA
        elif score >= 40:
            recomendacao = RecomendacaoEnum.NEUTRO
        else:
            recomendacao = RecomendacaoEnum.VENDA

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Macro Trading",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Investimento baseado em tendências macroeconômicas globais."
        )


# Integração com comunicação entre serviços
sys.path.append('/app/microservices/shared')
try:
    from shared.communication import service_client, validate_user_token, get_stock_data
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

# Endpoint para análise integrada
@app.post("/analyze/integrated")
async def analyze_integrated(request: AnalyzeRequest):
    """Análise integrada com dados externos"""
    try:
        # Obter dados da ação via serviço de dados
        if service_client:
            stock_data = await get_stock_data(request.symbol)
            
            # Converter dados para formato esperado
            dados_financeiros = DadosFinanceiros(
                symbol=request.symbol,
                pe_ratio=stock_data.get("pe_ratio"),
                price_to_book=stock_data.get("price_to_book"),
                debt_to_equity=stock_data.get("debt_to_equity"),
                roe=stock_data.get("roe"),
                current_ratio=stock_data.get("current_ratio"),
                dividend_yield=stock_data.get("dividend_yield"),
                payout_ratio=stock_data.get("payout_ratio"),
                earnings_growth=stock_data.get("earnings_growth"),
                revenue_growth=stock_data.get("revenue_growth"),
                profit_margin=stock_data.get("profit_margin"),
                beta=stock_data.get("beta"),
                market_cap=stock_data.get("market_cap"),
                free_cash_flow=stock_data.get("free_cash_flow")
            )
        else:
            # Fallback para dados simulados
            dados_financeiros = DadosFinanceiros(symbol=request.symbol)
        
        # Aplicar metodologia
        metodologia_class = METODOLOGIAS.get(request.methodology)
        if not metodologia_class:
            raise HTTPException(status_code=400, detail="Metodologia não encontrada")
        
        resultado = metodologia_class.analisar(dados_financeiros)
        
        # Publicar resultado no Kafka
        if kafka_producer:
            await kafka_producer.send_analysis_result(resultado.dict())
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro na análise integrada: {e}")
        raise HTTPException(status_code=500, detail=str(e))

