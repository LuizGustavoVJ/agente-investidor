import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

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

class AnaliseFinanceira:
    """Classe principal para análise financeira baseada nas metodologias dos grandes investidores"""
    
    @staticmethod
    def calcular_pe_ratio(price: float, earnings_per_share: float) -> Optional[float]:
        """Calcula o P/E ratio"""
        if earnings_per_share <= 0:
            return None
        return price / earnings_per_share
    
    @staticmethod
    def calcular_pb_ratio(price: float, book_value_per_share: float) -> Optional[float]:
        """Calcula o P/B ratio"""
        if book_value_per_share <= 0:
            return None
        return price / book_value_per_share
    
    @staticmethod
    def calcular_peg_ratio(pe_ratio: float, earnings_growth: float) -> Optional[float]:
        """Calcula o PEG ratio"""
        if earnings_growth <= 0 or pe_ratio <= 0:
            return None
        return pe_ratio / earnings_growth
    
    @staticmethod
    def calcular_roe(net_income: float, total_equity: float) -> Optional[float]:
        """Calcula o Return on Equity"""
        if total_equity <= 0:
            return None
        return (net_income / total_equity) * 100
    
    @staticmethod
    def calcular_roa(net_income: float, total_assets: float) -> Optional[float]:
        """Calcula o Return on Assets"""
        if total_assets <= 0:
            return None
        return (net_income / total_assets) * 100
    
    @staticmethod
    def calcular_debt_to_equity(total_debt: float, total_equity: float) -> Optional[float]:
        """Calcula a relação Dívida/Patrimônio"""
        if total_equity <= 0:
            return None
        return total_debt / total_equity
    
    @staticmethod
    def calcular_current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
        """Calcula o índice de liquidez corrente"""
        if current_liabilities <= 0:
            return None
        return current_assets / current_liabilities
    
    @staticmethod
    def calcular_margem_seguranca(preco_atual: float, valor_intrinseco: float) -> float:
        """Calcula a margem de segurança de Graham"""
        if valor_intrinseco <= 0:
            return 0
        return ((valor_intrinseco - preco_atual) / valor_intrinseco) * 100
    
    @staticmethod
    def analise_warren_buffett(dados: DadosFinanceiros) -> AnaliseResultado:
        """Análise baseada na metodologia de Warren Buffett"""
        score = 0
        pontos_fortes = []
        pontos_fracos = []
        
        # Critérios de Buffett
        # 1. P/E razoável (< 15 é bom, < 25 aceitável)
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 20
                pontos_fortes.append(f"P/E excelente: {dados.pe_ratio:.2f}")
            elif dados.pe_ratio < 25:
                score += 10
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")
        
        # 2. ROE alto (> 15% é bom)
        if dados.roe:
            if dados.roe > 15:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 10:
                score += 10
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")
        
        # 3. Dívida controlada (D/E < 0.5 é bom)
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.3:
                score += 15
                pontos_fortes.append(f"Dívida muito baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.5:
                score += 10
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")
        
        # 4. Margem de lucro (> 10% é bom)
        if dados.profit_margin:
            if dados.profit_margin > 15:
                score += 15
                pontos_fortes.append(f"Margem de lucro excelente: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 10:
                score += 10
                pontos_fortes.append(f"Margem de lucro boa: {dados.profit_margin:.2f}%")
            else:
                pontos_fracos.append(f"Margem de lucro baixa: {dados.profit_margin:.2f}%")
        
        # 5. Crescimento consistente
        if dados.earnings_growth:
            if dados.earnings_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento de lucros forte: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 5:
                score += 10
                pontos_fortes.append(f"Crescimento de lucros moderado: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento de lucros baixo: {dados.earnings_growth:.2f}%")
        
        # 6. Free Cash Flow positivo
        if dados.free_cash_flow and dados.free_cash_flow > 0:
            score += 15
            pontos_fortes.append("Free Cash Flow positivo")
        elif dados.free_cash_flow:
            pontos_fracos.append("Free Cash Flow negativo")
        
        # Determinar recomendação
        if score >= 70:
            recomendacao = "COMPRA"
        elif score >= 40:
            recomendacao = "NEUTRO"
        else:
            recomendacao = "VENDA"
        
        # Calcular preço alvo (método simplificado)
        preco_alvo = None
        if dados.earnings_per_share and dados.earnings_growth:
            # Preço alvo baseado em P/E futuro estimado
            pe_alvo = min(15, dados.earnings_growth)  # P/E conservador
            eps_futuro = dados.earnings_per_share * (1 + dados.earnings_growth / 100)
            preco_alvo = eps_futuro * pe_alvo
        
        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Warren Buffett - Value Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            preco_alvo=preco_alvo,
            justificativa=f"Análise baseada nos critérios de Buffett: empresas com vantagem competitiva, boa gestão e preço razoável."
        )
    
    @staticmethod
    def analise_benjamin_graham(dados: DadosFinanceiros) -> AnaliseResultado:
        """Análise baseada na metodologia de Benjamin Graham"""
        score = 0
        pontos_fortes = []
        pontos_fracos = []
        
        # Critérios de Graham
        # 1. P/E < 15
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 25
                pontos_fortes.append(f"P/E dentro do critério Graham: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E acima do critério Graham: {dados.pe_ratio:.2f}")
        
        # 2. P/B < 1.5
        if dados.pb_ratio:
            if dados.pb_ratio < 1.5:
                score += 20
                pontos_fortes.append(f"P/B excelente: {dados.pb_ratio:.2f}")
            elif dados.pb_ratio < 2.5:
                score += 10
                pontos_fortes.append(f"P/B aceitável: {dados.pb_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/B alto: {dados.pb_ratio:.2f}")
        
        # 3. Current Ratio > 2
        if dados.current_ratio:
            if dados.current_ratio > 2:
                score += 20
                pontos_fortes.append(f"Liquidez excelente: {dados.current_ratio:.2f}")
            elif dados.current_ratio > 1.5:
                score += 10
                pontos_fortes.append(f"Liquidez boa: {dados.current_ratio:.2f}")
            else:
                pontos_fracos.append(f"Liquidez baixa: {dados.current_ratio:.2f}")
        
        # 4. Debt/Equity < 0.5
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 20
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")
        
        # 5. Dividend Yield > 0 (empresas que pagam dividendos)
        if dados.dividend_yield and dados.dividend_yield > 0:
            score += 15
            pontos_fortes.append(f"Paga dividendos: {dados.dividend_yield:.2f}%")
        
        # Calcular margem de segurança
        margem_seguranca = None
        if dados.book_value_per_share:
            # Valor intrínseco simplificado de Graham
            valor_intrinseco = dados.book_value_per_share * 1.5  # Conservador
            margem_seguranca = AnaliseFinanceira.calcular_margem_seguranca(dados.price, valor_intrinseco)
            
            if margem_seguranca > 30:
                score += 20
                pontos_fortes.append(f"Excelente margem de segurança: {margem_seguranca:.1f}%")
            elif margem_seguranca > 15:
                score += 10
                pontos_fortes.append(f"Boa margem de segurança: {margem_seguranca:.1f}%")
            else:
                pontos_fracos.append(f"Margem de segurança insuficiente: {margem_seguranca:.1f}%")
        
        # Determinar recomendação
        if score >= 70:
            recomendacao = "COMPRA"
        elif score >= 40:
            recomendacao = "NEUTRO"
        else:
            recomendacao = "VENDA"
        
        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Benjamin Graham - Defensive Value",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            margem_seguranca=margem_seguranca,
            justificativa="Análise baseada nos critérios defensivos de Graham: segurança do principal e margem de segurança."
        )
    
    @staticmethod
    def analise_peter_lynch(dados: DadosFinanceiros) -> AnaliseResultado:
        """Análise baseada na metodologia de Peter Lynch"""
        score = 0
        pontos_fortes = []
        pontos_fracos = []
        
        # Critérios de Lynch
        # 1. PEG Ratio < 1 (ideal)
        if dados.peg_ratio:
            if dados.peg_ratio < 0.5:
                score += 30
                pontos_fortes.append(f"PEG excelente: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1:
                score += 20
                pontos_fortes.append(f"PEG bom: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1.5:
                score += 10
                pontos_fortes.append(f"PEG aceitável: {dados.peg_ratio:.2f}")
            else:
                pontos_fracos.append(f"PEG alto: {dados.peg_ratio:.2f}")
        
        # 2. Crescimento de receita > 10%
        if dados.revenue_growth:
            if dados.revenue_growth > 20:
                score += 25
                pontos_fortes.append(f"Crescimento de receita excelente: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento de receita bom: {dados.revenue_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento de receita baixo: {dados.revenue_growth:.2f}%")
        
        # 3. Crescimento de lucros > 15%
        if dados.earnings_growth:
            if dados.earnings_growth > 25:
                score += 25
                pontos_fortes.append(f"Crescimento de lucros excelente: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 15:
                score += 15
                pontos_fortes.append(f"Crescimento de lucros bom: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento de lucros baixo: {dados.earnings_growth:.2f}%")
        
        # 4. P/E razoável para o crescimento
        if dados.pe_ratio and dados.earnings_growth:
            pe_growth_ratio = dados.pe_ratio / dados.earnings_growth
            if pe_growth_ratio < 0.5:
                score += 20
                pontos_fortes.append(f"P/E baixo para o crescimento: {pe_growth_ratio:.2f}")
            elif pe_growth_ratio < 1:
                score += 10
                pontos_fortes.append(f"P/E razoável para o crescimento: {pe_growth_ratio:.2f}")
        
        # Determinar recomendação
        if score >= 70:
            recomendacao = "COMPRA"
        elif score >= 40:
            recomendacao = "NEUTRO"
        else:
            recomendacao = "VENDA"
        
        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Peter Lynch - Growth at Reasonable Price",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada nos critérios de Lynch: crescimento sustentável a preço razoável (PEG < 1)."
        )
    
    @staticmethod
    def analise_dividendos(dados: DadosFinanceiros) -> AnaliseResultado:
        """Análise focada em dividendos (Barsi/Geraldine Weiss)"""
        score = 0
        pontos_fortes = []
        pontos_fracos = []
        
        # Critérios para investimento em dividendos
        # 1. Dividend Yield > 4%
        if dados.dividend_yield:
            if dados.dividend_yield > 6:
                score += 30
                pontos_fortes.append(f"Dividend yield excelente: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 4:
                score += 20
                pontos_fortes.append(f"Dividend yield bom: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 2:
                score += 10
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Dividend yield baixo: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")
        
        # 2. Payout ratio sustentável (< 80%)
        if dados.earnings_per_share and dados.dividend_yield:
            dividend_per_share = dados.price * (dados.dividend_yield / 100)
            payout_ratio = (dividend_per_share / dados.earnings_per_share) * 100
            
            if payout_ratio < 60:
                score += 20
                pontos_fortes.append(f"Payout ratio sustentável: {payout_ratio:.1f}%")
            elif payout_ratio < 80:
                score += 10
                pontos_fortes.append(f"Payout ratio aceitável: {payout_ratio:.1f}%")
            else:
                pontos_fracos.append(f"Payout ratio alto: {payout_ratio:.1f}%")
        
        # 3. ROE > 12% (capacidade de gerar lucro)
        if dados.roe:
            if dados.roe > 15:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 12:
                score += 15
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")
        
        # 4. Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")
        
        # 5. Estabilidade (P/E não muito alto)
        if dados.pe_ratio:
            if dados.pe_ratio < 20:
                score += 15
                pontos_fortes.append(f"P/E estável: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")
        
        # Determinar recomendação
        if score >= 70:
            recomendacao = "COMPRA"
        elif score >= 40:
            recomendacao = "NEUTRO"
        else:
            recomendacao = "VENDA"
        
        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Foco em Dividendos - Barsi/Weiss",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise focada em renda passiva: dividend yield alto, payout sustentável e empresa sólida."
        )

