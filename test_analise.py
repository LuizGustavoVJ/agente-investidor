#!/usr/bin/env python3
"""
Script de teste para verificar se a análise de ações está funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.analise_financeira import AnaliseFinanceira, DadosFinanceiros
from src.data import get_simulated_data

def test_analise():
    print("🧪 Testando análise de ações...")
    
    # Testar com dados simulados da PETR4.SA
    symbol = "PETR4.SA"
    dados_simulados = get_simulated_data(symbol)
    
    if dados_simulados:
        print(f"✅ Dados simulados encontrados para {symbol}")
        print(f"   Preço: R$ {dados_simulados.get('regularMarketPrice')}")
        print(f"   Nome: {dados_simulados.get('longName')}")
    else:
        print(f"❌ Dados simulados não encontrados para {symbol}")
        return False
    
    # Criar objeto DadosFinanceiros
    dados_financeiros = DadosFinanceiros(
        symbol=symbol,
        price=dados_simulados.get('regularMarketPrice', 30.0),
        market_cap=dados_simulados.get('marketCap', 400000000000),
        pe_ratio=12.0,
        pb_ratio=1.5,
        peg_ratio=1.2,
        dividend_yield=5.0,
        roe=15.0,
        roa=8.0,
        debt_to_equity=0.4,
        current_ratio=1.8,
        free_cash_flow=100000000,
        revenue_growth=10.0,
        earnings_growth=12.0,
        profit_margin=15.0,
        operating_margin=20.0,
        book_value_per_share=20.0,
        earnings_per_share=2.5
    )
    
    print(f"✅ DadosFinanceiros criado com sucesso")
    
    # Testar análise Warren Buffett
    try:
        resultado = AnaliseFinanceira.analise_warren_buffett(dados_financeiros)
        print(f"✅ Análise Warren Buffett executada com sucesso")
        print(f"   Score: {resultado.score}/100")
        print(f"   Recomendação: {resultado.recomendacao}")
        print(f"   Metodologia: {resultado.metodologia_aplicada}")
        print(f"   Pontos fortes: {len(resultado.pontos_fortes)} itens")
        print(f"   Pontos fracos: {len(resultado.pontos_fracos)} itens")
        return True
    except Exception as e:
        print(f"❌ Erro na análise Warren Buffett: {e}")
        return False

if __name__ == "__main__":
    success = test_analise()
    if success:
        print("\n🎉 Todos os testes passaram! A análise está funcionando.")
    else:
        print("\n💥 Alguns testes falharam. Verifique os erros acima.")
    
    sys.exit(0 if success else 1)

