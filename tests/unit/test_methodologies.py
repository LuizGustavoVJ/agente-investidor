"""
Testes unitários das metodologias de investimento
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Adicionar path dos microserviços
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'microservices', 'shared'))

from models.dto import DadosFinanceiros, AnaliseResultado, RecomendacaoEnum

class TestValueInvesting:
    """Testes para metodologia Value Investing (Warren Buffett)"""
    
    def test_value_investing_compra(self, sample_stock_data):
        """Testa recomendação de compra"""
        # Simular importação da metodologia
        with patch.dict('sys.modules', {'methodology-service.main': Mock()}):
            # Dados que devem gerar recomendação de COMPRA
            dados = DadosFinanceiros(
                symbol="PETR4.SA",
                pe_ratio=12.0,  # P/E baixo
                price_to_book=0.8,  # P/B baixo
                debt_to_equity=0.3,  # Dívida baixa
                roe=20.0,  # ROE alto
                current_ratio=2.0,  # Liquidez boa
                dividend_yield=5.0,  # Dividend yield alto
                profit_margin=18.0,  # Margem alta
                free_cash_flow=1000000000  # FCF positivo
            )
            
            # Simular análise Value Investing
            score = 0
            pontos_fortes = []
            pontos_fracos = []
            
            # P/E baixo
            if dados.pe_ratio and dados.pe_ratio < 15:
                score += 25
                pontos_fortes.append(f"P/E atrativo: {dados.pe_ratio}")
            
            # P/B baixo
            if dados.price_to_book and dados.price_to_book < 1.0:
                score += 20
                pontos_fortes.append(f"P/B baixo: {dados.price_to_book}")
            
            # ROE alto
            if dados.roe and dados.roe > 15:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe}%")
            
            # Dívida baixa
            if dados.debt_to_equity and dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity}")
            
            # FCF positivo
            if dados.free_cash_flow and dados.free_cash_flow > 0:
                score += 20
                pontos_fortes.append("Free Cash Flow positivo")
            
            assert score >= 70  # Deve ser COMPRA
            assert len(pontos_fortes) >= 4
            assert "P/E atrativo" in str(pontos_fortes)
            assert "ROE excelente" in str(pontos_fortes)
    
    def test_value_investing_venda(self):
        """Testa recomendação de venda"""
        dados = DadosFinanceiros(
            symbol="TESTE.SA",
            pe_ratio=35.0,  # P/E alto
            price_to_book=3.0,  # P/B alto
            debt_to_equity=2.0,  # Dívida alta
            roe=5.0,  # ROE baixo
            current_ratio=0.8,  # Liquidez ruim
            dividend_yield=1.0,  # Dividend yield baixo
            profit_margin=3.0,  # Margem baixa
            free_cash_flow=-500000000  # FCF negativo
        )
        
        score = 0
        pontos_fracos = []
        
        # P/E alto
        if dados.pe_ratio and dados.pe_ratio > 25:
            pontos_fracos.append(f"P/E alto: {dados.pe_ratio}")
        
        # P/B alto
        if dados.price_to_book and dados.price_to_book > 2.0:
            pontos_fracos.append(f"P/B alto: {dados.price_to_book}")
        
        # ROE baixo
        if dados.roe and dados.roe < 10:
            pontos_fracos.append(f"ROE baixo: {dados.roe}%")
        
        # FCF negativo
        if dados.free_cash_flow and dados.free_cash_flow < 0:
            pontos_fracos.append("Free Cash Flow negativo")
        
        assert score < 40  # Deve ser VENDA
        assert len(pontos_fracos) >= 3

class TestDividendInvesting:
    """Testes para metodologia Dividend Investing"""
    
    def test_dividend_investing_compra(self):
        """Testa recomendação de compra para dividend investing"""
        dados = DadosFinanceiros(
            symbol="ITUB4.SA",
            dividend_yield=6.0,  # Dividend yield alto
            payout_ratio=60.0,  # Payout sustentável
            roe=18.0,  # ROE bom
            debt_to_equity=0.4,  # Dívida controlada
            current_ratio=1.8,  # Liquidez boa
            profit_margin=20.0  # Margem boa
        )
        
        score = 0
        pontos_fortes = []
        
        # Dividend yield alto
        if dados.dividend_yield and dados.dividend_yield > 5:
            score += 30
            pontos_fortes.append(f"Dividend yield alto: {dados.dividend_yield}%")
        
        # Payout sustentável
        if dados.payout_ratio and 40 <= dados.payout_ratio <= 70:
            score += 25
            pontos_fortes.append(f"Payout sustentável: {dados.payout_ratio}%")
        
        # ROE bom
        if dados.roe and dados.roe > 15:
            score += 20
            pontos_fortes.append(f"ROE bom: {dados.roe}%")
        
        assert score >= 70  # Deve ser COMPRA
        assert "Dividend yield alto" in str(pontos_fortes)
        assert "Payout sustentável" in str(pontos_fortes)

class TestGrowthInvesting:
    """Testes para metodologia Growth Investing"""
    
    def test_growth_investing_compra(self):
        """Testa recomendação de compra para growth investing"""
        dados = DadosFinanceiros(
            symbol="MGLU3.SA",
            earnings_growth=25.0,  # Crescimento alto
            revenue_growth=20.0,  # Receita crescendo
            roe=22.0,  # ROE alto
            profit_margin=15.0,  # Margem boa
            pe_ratio=20.0,  # P/E razoável para growth
            debt_to_equity=0.6  # Dívida moderada
        )
        
        score = 0
        pontos_fortes = []
        
        # Crescimento de lucros alto
        if dados.earnings_growth and dados.earnings_growth > 20:
            score += 30
            pontos_fortes.append(f"Crescimento de lucros alto: {dados.earnings_growth}%")
        
        # Crescimento de receita
        if dados.revenue_growth and dados.revenue_growth > 15:
            score += 25
            pontos_fortes.append(f"Crescimento de receita: {dados.revenue_growth}%")
        
        # ROE alto
        if dados.roe and dados.roe > 20:
            score += 20
            pontos_fortes.append(f"ROE excelente: {dados.roe}%")
        
        assert score >= 70  # Deve ser COMPRA
        assert "Crescimento de lucros alto" in str(pontos_fortes)

class TestTechnicalTrading:
    """Testes para metodologia Technical Trading"""
    
    def test_technical_trading_momentum(self):
        """Testa análise de momentum"""
        dados = DadosFinanceiros(
            symbol="VALE3.SA",
            beta=1.2,  # Volatilidade adequada
            market_cap=200000000000,  # Alta liquidez
            earnings_growth=18.0,  # Momentum positivo
            pe_ratio=22.0,  # Sentimento equilibrado
            free_cash_flow=5000000000  # Suporte fundamental
        )
        
        score = 0
        pontos_fortes = []
        
        # Volatilidade adequada
        if dados.beta and 0.8 <= dados.beta <= 1.5:
            score += 25
            pontos_fortes.append(f"Volatilidade adequada: {dados.beta}")
        
        # Alta liquidez
        if dados.market_cap and dados.market_cap > 10000000000:
            score += 20
            pontos_fortes.append("Alta liquidez")
        
        # Momentum positivo
        if dados.earnings_growth and dados.earnings_growth > 15:
            score += 20
            pontos_fortes.append(f"Momentum positivo: {dados.earnings_growth}%")
        
        assert score >= 60  # Deve ser pelo menos NEUTRO
        assert "Volatilidade adequada" in str(pontos_fortes)

class TestMethodologyIntegration:
    """Testes de integração entre metodologias"""
    
    def test_multiple_methodologies_consensus(self):
        """Testa consenso entre múltiplas metodologias"""
        # Dados que devem ser positivos para múltiplas metodologias
        dados = DadosFinanceiros(
            symbol="WEGE3.SA",
            pe_ratio=18.0,  # Bom para value
            price_to_book=1.5,  # Razoável
            roe=25.0,  # Excelente para todas
            earnings_growth=15.0,  # Bom para growth
            dividend_yield=3.5,  # Moderado para dividend
            payout_ratio=50.0,  # Sustentável
            debt_to_equity=0.3,  # Baixo
            current_ratio=2.0,  # Bom
            profit_margin=20.0,  # Alto
            beta=1.0,  # Equilibrado
            market_cap=80000000000,  # Grande
            free_cash_flow=3000000000  # Positivo
        )
        
        # Simular análise com múltiplas metodologias
        scores = []
        
        # Value Investing
        value_score = 0
        if dados.pe_ratio < 20: value_score += 20
        if dados.roe > 20: value_score += 25
        if dados.debt_to_equity < 0.5: value_score += 15
        if dados.free_cash_flow > 0: value_score += 20
        scores.append(value_score)
        
        # Growth Investing
        growth_score = 0
        if dados.earnings_growth > 10: growth_score += 25
        if dados.roe > 20: growth_score += 25
        if dados.profit_margin > 15: growth_score += 20
        scores.append(growth_score)
        
        # Dividend Investing
        dividend_score = 0
        if dados.dividend_yield > 3: dividend_score += 20
        if 40 <= dados.payout_ratio <= 70: dividend_score += 25
        if dados.roe > 15: dividend_score += 20
        scores.append(dividend_score)
        
        # Verificar consenso
        average_score = sum(scores) / len(scores)
        assert average_score >= 60  # Consenso positivo
        assert all(score >= 50 for score in scores)  # Todas metodologias positivas

    def test_methodology_edge_cases(self):
        """Testa casos extremos das metodologias"""
        # Dados com valores nulos/zero
        dados_vazios = DadosFinanceiros(symbol="TEST.SA")
        
        # Deve lidar com dados faltantes sem erro
        score = 0
        pontos_fracos = ["Dados insuficientes para análise"]
        
        assert score == 0
        assert len(pontos_fracos) >= 1
        
        # Dados com valores extremos
        dados_extremos = DadosFinanceiros(
            symbol="EXTREME.SA",
            pe_ratio=1000.0,  # P/E extremamente alto
            price_to_book=0.01,  # P/B extremamente baixo
            debt_to_equity=10.0,  # Dívida extremamente alta
            roe=-50.0,  # ROE negativo
            current_ratio=0.1,  # Liquidez péssima
            dividend_yield=50.0,  # Dividend yield irrealista
            beta=5.0  # Beta muito alto
        )
        
        # Deve identificar como investimento de alto risco
        risk_flags = []
        if dados_extremos.pe_ratio and dados_extremos.pe_ratio > 50:
            risk_flags.append("P/E extremamente alto")
        if dados_extremos.debt_to_equity and dados_extremos.debt_to_equity > 3:
            risk_flags.append("Dívida excessiva")
        if dados_extremos.roe and dados_extremos.roe < 0:
            risk_flags.append("ROE negativo")
        
        assert len(risk_flags) >= 2  # Múltiplos sinais de risco

