from typing import Optional
from .dto import (
    DadosFinanceiros, AnaliseResultado
)
from .investidor import (
    METODOLOGIAS_MAP
)

class AnaliseFinanceira:
    """Classe principal para análise financeira baseada nas metodologias dos grandes investidores"""

    @staticmethod
    def calcular_pe_ratio(price: float, earnings_per_share: float) -> Optional[float]:
        if earnings_per_share <= 0:
            return None
        return price / earnings_per_share

    @staticmethod
    def calcular_pb_ratio(
        price: float, book_value_per_share: float
    ) -> Optional[float]:
        if book_value_per_share <= 0:
            return None
        return price / book_value_per_share

    @staticmethod
    def calcular_peg_ratio(
        pe_ratio: float, earnings_growth: float
    ) -> Optional[float]:
        if earnings_growth <= 0 or pe_ratio <= 0:
            return None
        return pe_ratio / earnings_growth

    @staticmethod
    def calcular_roe(
        net_income: float, total_equity: float
    ) -> Optional[float]:
        if total_equity <= 0:
            return None
        return (net_income / total_equity) * 100

    @staticmethod
    def calcular_roa(
        net_income: float, total_assets: float
    ) -> Optional[float]:
        if total_assets <= 0:
            return None
        return (net_income / total_assets) * 100

    @staticmethod
    def calcular_debt_to_equity(
        total_debt: float, total_equity: float
    ) -> Optional[float]:
        if total_equity <= 0:
            return None
        return total_debt / total_equity

    @staticmethod
    def calcular_current_ratio(
        current_assets: float, current_liabilities: float
    ) -> Optional[float]:
        if current_liabilities <= 0:
            return None
        return current_assets / current_liabilities

    @staticmethod
    def analisar(
        metodologia_nome: str,
        dados: DadosFinanceiros
    ) -> AnaliseResultado:
        """
        Executa a análise financeira usando a metodologia informada.
        :param metodologia_nome: Nome da metodologia
            (ex: "Value Investing", "Defensive Value", etc)
        :param dados: DadosFinanceiros
        :return: AnaliseResultado
        """
        metodologia = METODOLOGIAS_MAP.get(metodologia_nome)
        if metodologia is None:
            raise ValueError(
                f"Metodologia '{metodologia_nome}' não encontrada."
            )
        return metodologia.analisar(dados)

