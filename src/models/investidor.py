from dataclasses import dataclass
from typing import List
from enum import Enum
from .metodologias import (
    ValueInvesting, GrowthInvesting, DividendInvesting, TechnicalTrading,
    MacroTrading, ActivistInvesting, PassiveInvesting, DefensiveValue,
    GrowthAtReasonablePrice, IncomeInvesting
)

class TipoInvestidor(Enum):
    VALUE = "value"
    GROWTH = "growth"
    DIVIDEND = "dividend"
    TECHNICAL = "technical"
    MACRO = "macro"
    ACTIVIST = "activist"
    PASSIVE = "passive"

@dataclass
class PerfilInvestidor:
    nome: str
    tipo: TipoInvestidor
    metodologia: str
    foco_principal: str
    indicadores_chave: List[str]
    exemplos_investimentos: List[str]
    sites_recomendados: List[str]
    livros_recomendados: List[str]

# Utilitários para acessar as metodologias
METODOLOGIAS = [
    ValueInvesting,
    GrowthInvesting,
    DividendInvesting,
    TechnicalTrading,
    MacroTrading,
    ActivistInvesting,
    PassiveInvesting,
    DefensiveValue,
    GrowthAtReasonablePrice,
    IncomeInvesting,
]

METODOLOGIAS_MAP = {m.nome: m for m in METODOLOGIAS}

