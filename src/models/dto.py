from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DadosFinanceiros:
    """Estrutura para dados financeiros de uma empresa"""
    symbol: str
    price: float
    market_cap: float
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    book_value_per_share: Optional[float] = None
    earnings_per_share: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_debt: Optional[float] = None
    total_equity: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None

@dataclass
class AnaliseResultado:
    """Resultado de uma análise de investimento"""
    symbol: str
    score: float  # 0-100
    recomendacao: str  # "COMPRA", "VENDA", "NEUTRO"
    metodologia_aplicada: str
    pontos_fortes: List[str]
    pontos_fracos: List[str]
    preco_alvo: Optional[float] = None
    margem_seguranca: Optional[float] = None
    justificativa: str = "" 