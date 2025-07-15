"""
Serviço de Metodologias de Investimento - Agente Investidor
Responsável por aplicar diferentes metodologias de análise de investimentos
"""

import os
import sys
import uvicorn
import httpx
import json
import time
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, start_http_server
import structlog
import redis
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
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
REQUEST_COUNT = Counter('methodology_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('methodology_request_duration_seconds', 'Request duration')
ANALYSIS_COUNT = Counter('methodology_analysis_total', 'Total analyses', ['methodology', 'recommendation'])

# Redis connection with retry logic
def get_redis_client():
    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=2,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        client.ping()
        logger.info("Redis conectado com sucesso")
        return client
    except Exception as e:
        logger.error(f"Erro ao conectar ao Redis: {e}")
        return None

redis_client = get_redis_client()

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

# Enums
class RecomendacaoEnum(str, Enum):
    COMPRA = "COMPRA"
    VENDA = "VENDA"
    NEUTRO = "NEUTRO"

# Models
class DadosFinanceiros(BaseModel):
    symbol: str
    price: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    free_cash_flow: Optional[float] = None
    beta: Optional[float] = None
    peg_ratio: Optional[float] = None

class AnaliseResultado(BaseModel):
    symbol: str
    score: int
    recomendacao: RecomendacaoEnum
    metodologia_aplicada: str
    pontos_fortes: List[str] = Field(default_factory=list)
    pontos_fracos: List[str] = Field(default_factory=list)
    justificativa: str

class MetodologiaInfo(BaseModel):
    nome: str
    descricao: str
    indicadores: List[str]

class AnaliseRequest(BaseModel):
    symbol: str
    metodologia: str

class AnaliseResponse(BaseModel):
    symbol: str
    metodologia: str
    resultado: AnaliseResultado
    timestamp: datetime

class ComparacaoRequest(BaseModel):
    symbol: str
    metodologias: List[str]

class ComparacaoResponse(BaseModel):
    symbol: str
    resultados: Dict[str, AnaliseResultado]
    melhor_metodologia: str
    timestamp: datetime

# Configuração
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://data-service:8002")

# Metodologias de Investimento
class ValueInvesting:
    nome = "warren_buffett"
    descricao = "Foco em empresas sólidas, vantagem competitiva (moat), gestão de qualidade, geração de caixa e compra com margem de segurança."
    indicadores = ["P/E ratio", "ROE", "Debt/Equity", "Free Cash Flow", "Moat"]
    
    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # P/E baixo
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 25
                pontos_fortes.append(f"P/E baixo: {dados.pe_ratio:.2f}")
            elif dados.pe_ratio < 20:
                score += 15
                pontos_fortes.append(f"P/E moderado: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")

        # ROE alto
        if dados.roe:
            if dados.roe > 20:
                score += 25
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 15:
                score += 15
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 20
                pontos_fortes.append(f"Dívida baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 1.0:
                score += 10
                pontos_fortes.append(f"Dívida moderada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

        # Free Cash Flow positivo
        if dados.free_cash_flow:
            if dados.free_cash_flow > 0:
                score += 20
                pontos_fortes.append(f"FCF positivo: {dados.free_cash_flow:.2f}")
            else:
                pontos_fracos.append(f"FCF negativo: {dados.free_cash_flow:.2f}")

        # Margem de lucro
        if dados.profit_margin:
            if dados.profit_margin > 15:
                score += 10
                pontos_fortes.append(f"Margem alta: {dados.profit_margin:.2f}%")

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
            justificativa="Foco em empresas sólidas com vantagem competitiva."
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
        if dados.pb_ratio:
            if dados.pb_ratio < 1.0:
                score += 30
                pontos_fortes.append(f"P/B baixo: {dados.pb_ratio:.2f}")
            elif dados.pb_ratio < 1.5:
                score += 20
                pontos_fortes.append(f"P/B moderado: {dados.pb_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/B alto: {dados.pb_ratio:.2f}")

        # Liquidez alta
        if dados.current_ratio:
            if dados.current_ratio > 2.0:
                score += 25
                pontos_fortes.append(f"Liquidez excelente: {dados.current_ratio:.2f}")
            elif dados.current_ratio > 1.5:
                score += 15
                pontos_fortes.append(f"Liquidez boa: {dados.current_ratio:.2f}")
            else:
                pontos_fracos.append(f"Liquidez baixa: {dados.current_ratio:.2f}")

        # Dívida baixa
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.3:
                score += 25
                pontos_fortes.append(f"Dívida muito baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Dívida baixa: {dados.debt_to_equity:.2f}")

        # Dividend Yield
        if dados.dividend_yield:
            if dados.dividend_yield > 3:
                score += 20
                pontos_fortes.append(f"Dividend yield alto: {dados.dividend_yield:.2f}%")

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
            justificativa="Estratégia conservadora focando em segurança."
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

        # PEG ratio baixo
        if dados.peg_ratio:
            if dados.peg_ratio < 1.0:
                score += 30
                pontos_fortes.append(f"PEG excelente: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1.5:
                score += 20
                pontos_fortes.append(f"PEG bom: {dados.peg_ratio:.2f}")
            else:
                pontos_fracos.append(f"PEG alto: {dados.peg_ratio:.2f}")

        # Crescimento de lucros
        if dados.earnings_growth:
            if dados.earnings_growth > 20:
                score += 25
                pontos_fortes.append(f"Crescimento alto: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento moderado: {dados.earnings_growth:.2f}%")

        # Crescimento de receita
        if dados.revenue_growth:
            if dados.revenue_growth > 15:
                score += 20
                pontos_fortes.append(f"Crescimento de receita: {dados.revenue_growth:.2f}%")

        # ROE alto
        if dados.roe and dados.roe > 15:
            score += 15
            pontos_fortes.append(f"ROE alto: {dados.roe:.2f}%")

        # P/E razoável
        if dados.pe_ratio:
            if 15 <= dados.pe_ratio <= 25:
                score += 10
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")

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
            justificativa="Crescimento sólido a preços razoáveis."
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

        # Dividend Yield alto
        if dados.dividend_yield:
            if dados.dividend_yield > 4:
                score += 30
                pontos_fortes.append(f"Dividend yield alto: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 2:
                score += 20
                pontos_fortes.append(f"Dividend yield bom: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Dividend yield baixo: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")

        # Payout Ratio sustentável
        if dados.payout_ratio:
            if 40 <= dados.payout_ratio <= 70:
                score += 25
                pontos_fortes.append(f"Payout sustentável: {dados.payout_ratio:.2f}%")
            elif dados.payout_ratio < 80:
                score += 15
                pontos_fortes.append(f"Payout aceitável: {dados.payout_ratio:.2f}%")
            else:
                pontos_fracos.append(f"Payout alto: {dados.payout_ratio:.2f}%")

        # Free Cash Flow positivo
        if dados.free_cash_flow:
            if dados.free_cash_flow > 0:
                score += 20
                pontos_fortes.append(f"FCF positivo: {dados.free_cash_flow:.2f}")
            else:
                pontos_fracos.append(f"FCF negativo: {dados.free_cash_flow:.2f}")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Dívida baixa: {dados.debt_to_equity:.2f}")

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
            metodologia_aplicada="Dividend Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Foco em dividendos consistentes e crescentes."
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

        # Crescimento de receita alto
        if dados.revenue_growth:
            if dados.revenue_growth > 25:
                score += 30
                pontos_fortes.append(f"Crescimento alto: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 15:
                score += 20
                pontos_fortes.append(f"Crescimento bom: {dados.revenue_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento baixo: {dados.revenue_growth:.2f}%")

        # Crescimento de lucros
        if dados.earnings_growth:
            if dados.earnings_growth > 30:
                score += 25
                pontos_fortes.append(f"Crescimento de lucros alto: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 15:
                score += 15
                pontos_fortes.append(f"Crescimento de lucros bom: {dados.earnings_growth:.2f}%")

        # ROE alto
        if dados.roe:
            if dados.roe > 25:
                score += 20
                pontos_fortes.append(f"ROE muito alto: {dados.roe:.2f}%")
            elif dados.roe > 15:
                score += 15
                pontos_fortes.append(f"ROE alto: {dados.roe:.2f}%")

        # Margem de lucro
        if dados.profit_margin:
            if dados.profit_margin > 20:
                score += 15
                pontos_fortes.append(f"Margem alta: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 10:
                score += 10
                pontos_fortes.append(f"Margem boa: {dados.profit_margin:.2f}%")

        # P/E alto é aceitável para growth
        if dados.pe_ratio:
            if dados.pe_ratio > 30:
                score += 10
                pontos_fortes.append(f"P/E premium aceitável: {dados.pe_ratio:.2f}")

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
            justificativa="Foco em alto crescimento e potencial."
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

        # Volatilidade alta é positiva para trading
        volatilidade = getattr(dados, 'volatilidade', 0.03)
        if volatilidade > 0.025:
            score += 30
            pontos_fortes.append(f"Volatilidade alta: {volatilidade*100:.2f}%")
        else:
            pontos_fracos.append(f"Volatilidade baixa: {volatilidade*100:.2f}%")

        # Liquidez (simulação)
        liquidez = getattr(dados, 'liquidez', 1e7)
        if liquidez > 1e6:
            score += 25
            pontos_fortes.append(f"Alta liquidez: R$ {liquidez:,.0f}")
        else:
            pontos_fracos.append(f"Liquidez baixa: R$ {liquidez:,.0f}")

        # Tendência (simulação)
        tendencia = getattr(dados, 'tendencia', 1)
        if tendencia > 0:
            score += 20
            pontos_fortes.append("Tendência de alta identificada")
        else:
            pontos_fracos.append("Sem tendência clara")

        # Volume alto
        volume = getattr(dados, 'volume', 1e6)
        if volume > 5e5:
            score += 15
            pontos_fortes.append(f"Volume alto: {volume:,.0f}")
        else:
            pontos_fracos.append(f"Volume baixo: {volume:,.0f}")

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
            justificativa="Análise baseada em padrões técnicos e volatilidade."
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

        # Exposição internacional
        exposicao_internacional = getattr(dados, 'exposicao_internacional', 0.3)
        if exposicao_internacional > 0.2:
            score += 25
            pontos_fortes.append(f"Exposição internacional: {exposicao_internacional*100:.1f}%")
        else:
            pontos_fracos.append(f"Baixa exposição internacional: {exposicao_internacional*100:.1f}%")

        # Sensibilidade a juros
        sensibilidade_juros = getattr(dados, 'sensibilidade_juros', 0.5)
        if sensibilidade_juros < 0.3:
            score += 20
            pontos_fortes.append("Baixa sensibilidade a juros")
        else:
            pontos_fracos.append("Alta sensibilidade a juros")

        # Diversificação setorial
        diversificacao_setorial = getattr(dados, 'diversificacao_setorial', 0.6)
        if diversificacao_setorial > 0.5:
            score += 20
            pontos_fortes.append("Boa diversificação setorial")
        else:
            pontos_fracos.append("Baixa diversificação setorial")

        # Exposição a commodities
        exposicao_commodities = getattr(dados, 'exposicao_commodities', 0.2)
        if exposicao_commodities > 0.1:
            score += 15
            pontos_fortes.append(f"Exposição a commodities: {exposicao_commodities*100:.1f}%")

        # Beta de mercado
        if dados.beta:
            if 0.8 <= dados.beta <= 1.2:
                score += 20
                pontos_fortes.append(f"Beta equilibrado: {dados.beta:.2f}")
            else:
                pontos_fracos.append(f"Beta desequilibrado: {dados.beta:.2f}")

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
            justificativa="Análise baseada em tendências macroeconômicas globais."
        )

class ActivistInvesting:
    nome = "activist_investing"
    descricao = "Investimento ativista para influenciar mudanças corporativas."
    indicadores = ["Undervaluation", "Management Issues", "Asset Value", "Governance"]
    
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
        if dados.pb_ratio:
            if dados.pb_ratio < 1.0:
                score += 20
                pontos_fortes.append(f"P/B baixo - subvalorizada: {dados.pb_ratio:.2f}")
            elif dados.pb_ratio < 1.5:
                score += 15
                pontos_fortes.append(f"P/B atrativo: {dados.pb_ratio:.2f}")

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
            metodologia_aplicada="Activist Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Busca empresas com potencial de reestruturação e melhoria de governança."
        )

# Dicionário de metodologias (definido após todas as classes)
def get_metodologias():
    return {
        "warren_buffett": ValueInvesting,
        "benjamin_graham": DefensiveValue,
        "peter_lynch": GrowthAtReasonablePrice,
        "dividend_investing": DividendInvesting,
        "growth_investing": GrowthInvesting,
        "income_investing": IncomeInvesting,
        "passive_investing": PassiveInvesting,
        "technical_trading": TechnicalTrading,
        "macro_trading": MacroTrading,
        "activist_investing": ActivistInvesting,
    }

METODOLOGIAS = get_metodologias()

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
        "redis_connected": redis_client is not None
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
        port=8004,
        log_config=None  # Usar nosso logging estruturado
    ) 