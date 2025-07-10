"""
DTOs compartilhados entre microserviços
Baseado na estrutura existente do projeto
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RecomendacaoEnum(str, Enum):
    COMPRA = "COMPRA"
    VENDA = "VENDA"
    NEUTRO = "NEUTRO"

class DadosFinanceiros(BaseModel):
    """DTO para dados financeiros de uma ação"""
    symbol: str
    name: Optional[str] = None
    
    # Preços
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    
    # Volume e capitalização
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    
    # Indicadores fundamentalistas
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    price_to_book: Optional[float] = None  # Alias para pb_ratio
    ps_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    peg_ratio: Optional[float] = None
    
    # Rentabilidade
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic: Optional[float] = None
    profit_margin: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    
    # Fluxo de caixa
    free_cash_flow: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    fcf_yield: Optional[float] = None
    
    # Endividamento
    debt_to_equity: Optional[float] = None
    debt_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    
    # Dividendos
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    
    # Crescimento
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    
    # Risco
    beta: Optional[float] = None
    volatility: Optional[float] = None
    
    # Setor
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Timestamp
    timestamp: Optional[datetime] = None

class AnaliseResultado(BaseModel):
    """DTO para resultado de análise de metodologia"""
    metodologia: str
    symbol: str
    score: float = Field(..., ge=0, le=100, description="Score de 0 a 100")
    recomendacao: RecomendacaoEnum
    pontos_fortes: List[str] = []
    pontos_fracos: List[str] = []
    observacoes: List[str] = []
    preco_alvo: Optional[float] = None
    margem_seguranca: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MetodologiaInfo(BaseModel):
    """DTO para informações sobre uma metodologia"""
    nome: str
    descricao: str
    indicadores: List[str]
    exemplos: List[str]
    referencias: List[str]
    autor: Optional[str] = None
    tipo: Optional[str] = None

class AnaliseRequest(BaseModel):
    """DTO para requisição de análise"""
    symbol: str
    metodologias: Optional[List[str]] = None  # Se None, analisa todas
    dados_financeiros: Optional[DadosFinanceiros] = None  # Se None, busca automaticamente

class AnaliseResponse(BaseModel):
    """DTO para resposta de análise"""
    symbol: str
    resultados: List[AnaliseResultado]
    resumo: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ComparacaoRequest(BaseModel):
    """DTO para comparação entre metodologias"""
    symbols: List[str]
    metodologia: str

class ComparacaoResponse(BaseModel):
    """DTO para resposta de comparação"""
    metodologia: str
    resultados: List[AnaliseResultado]
    ranking: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BacktestRequest(BaseModel):
    """DTO para requisição de backtest"""
    metodologia: str
    symbols: List[str]
    periodo_inicio: datetime
    periodo_fim: datetime
    capital_inicial: float = 100000.0

class BacktestResponse(BaseModel):
    """DTO para resposta de backtest"""
    metodologia: str
    periodo: Dict[str, datetime]
    capital_inicial: float
    capital_final: float
    retorno_total: float
    retorno_anualizado: float
    volatilidade: float
    sharpe_ratio: float
    max_drawdown: float
    trades: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

