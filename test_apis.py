#!/usr/bin/env python3
"""
Script de teste para as APIs financeiras do agente investidor
"""

import sys
import os
sys.path.append('/opt/.manus/.sandbox-runtime')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_api import ApiClient
from src.models.analise_financeira import AnaliseFinanceira, DadosFinanceiros

def test_yahoo_finance_apis():
    """Testa as APIs do Yahoo Finance"""
    print("🔍 Testando APIs do Yahoo Finance...")
    
    client = ApiClient()
    
    # Teste 1: Perfil de empresa brasileira
    print("\n📊 Teste 1: Perfil da Petrobras (PETR4.SA)")
    try:
        profile = client.call_api('YahooFinance/get_stock_profile', query={
            'symbol': 'PETR4.SA',
            'region': 'BR',
            'lang': 'pt-BR'
        })
        
        if profile and 'quoteSummary' in profile:
            result = profile['quoteSummary']['result']
            if result and len(result) > 0 and 'summaryProfile' in result[0]:
                summary = result[0]['summaryProfile']
                print(f"✅ Empresa: {summary.get('longBusinessSummary', 'N/A')[:100]}...")
                print(f"✅ Setor: {summary.get('sector', 'N/A')}")
                print(f"✅ Indústria: {summary.get('industry', 'N/A')}")
                print(f"✅ Website: {summary.get('website', 'N/A')}")
            else:
                print("⚠️ Dados de perfil não encontrados")
        else:
            print("❌ Erro ao obter perfil da empresa")
    except Exception as e:
        print(f"❌ Erro no teste de perfil: {e}")
    
    # Teste 2: Dados de gráfico
    print("\n📈 Teste 2: Dados de gráfico da Petrobras")
    try:
        chart = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': 'PETR4.SA',
            'region': 'BR',
            'interval': '1d',
            'range': '1mo'
        })
        
        if chart and 'chart' in chart:
            result = chart['chart']['result']
            if result and len(result) > 0:
                meta = result[0]['meta']
                print(f"✅ Preço atual: R$ {meta.get('regularMarketPrice', 'N/A')}")
                print(f"✅ Moeda: {meta.get('currency', 'N/A')}")
                print(f"✅ Exchange: {meta.get('exchangeName', 'N/A')}")
                print(f"✅ Volume: {meta.get('regularMarketVolume', 'N/A'):,}")
                
                # Verificar dados históricos
                timestamps = result[0].get('timestamp', [])
                print(f"✅ Dados históricos: {len(timestamps)} pontos")
            else:
                print("⚠️ Dados de gráfico não encontrados")
        else:
            print("❌ Erro ao obter dados de gráfico")
    except Exception as e:
        print(f"❌ Erro no teste de gráfico: {e}")
    
    # Teste 3: Insights
    print("\n🎯 Teste 3: Insights da Petrobras")
    try:
        insights = client.call_api('YahooFinance/get_stock_insights', query={
            'symbol': 'PETR4.SA'
        })
        
        if insights and 'finance' in insights:
            result = insights['finance']['result']
            print(f"✅ Insights obtidos para: {result.get('symbol', 'N/A')}")
            
            # Verificar se há dados de recomendação
            if 'recommendation' in result:
                rec = result['recommendation']
                print(f"✅ Recomendação: {rec.get('rating', 'N/A')}")
                print(f"✅ Preço alvo: {rec.get('targetPrice', 'N/A')}")
        else:
            print("⚠️ Insights não disponíveis")
    except Exception as e:
        print(f"❌ Erro no teste de insights: {e}")

def test_worldbank_apis():
    """Testa as APIs do Banco Mundial"""
    print("\n🌍 Testando APIs do Banco Mundial...")
    
    client = ApiClient()
    
    # Teste 1: PIB do Brasil
    print("\n📊 Teste 1: PIB do Brasil")
    try:
        gdp = client.call_api('DataBank/indicator_data', query={
            'indicator': 'NY.GDP.MKTP.CD',
            'country': 'BRA'
        })
        
        if gdp and 'data' in gdp:
            print(f"✅ País: {gdp.get('countryName', 'N/A')}")
            print(f"✅ Indicador: {gdp.get('indicatorName', 'N/A')}")
            
            # Mostrar dados recentes
            data = gdp['data']
            recent_years = ['2022', '2021', '2020', '2019']
            for year in recent_years:
                if year in data and data[year]:
                    value = data[year] / 1e12  # Converter para trilhões
                    print(f"✅ {year}: US$ {value:.2f} trilhões")
                    break
        else:
            print("❌ Erro ao obter dados do PIB")
    except Exception as e:
        print(f"❌ Erro no teste do PIB: {e}")
    
    # Teste 2: Lista de indicadores
    print("\n📋 Teste 2: Lista de indicadores econômicos")
    try:
        indicators = client.call_api('DataBank/indicator_list', query={
            'q': 'inflation',
            'pageSize': 5
        })
        
        if indicators and 'items' in indicators:
            print(f"✅ Total de indicadores encontrados: {indicators.get('total', 0)}")
            print("✅ Primeiros indicadores de inflação:")
            for item in indicators['items'][:3]:
                print(f"   • {item['indicatorCode']}: {item['indicatorName']}")
        else:
            print("❌ Erro ao obter lista de indicadores")
    except Exception as e:
        print(f"❌ Erro no teste de indicadores: {e}")

def test_analise_financeira():
    """Testa as análises financeiras"""
    print("\n🧮 Testando Análises Financeiras...")
    
    # Criar dados fictícios para teste
    dados_teste = DadosFinanceiros(
        symbol="TESTE4.SA",
        price=50.0,
        market_cap=10000000000,  # 10 bilhões
        pe_ratio=12.5,
        pb_ratio=1.2,
        peg_ratio=0.8,
        dividend_yield=5.5,
        roe=18.0,
        roa=8.5,
        debt_to_equity=0.3,
        current_ratio=2.1,
        free_cash_flow=500000000,  # 500 milhões
        revenue_growth=12.0,
        earnings_growth=15.0,
        profit_margin=12.0,
        operating_margin=15.0,
        book_value_per_share=42.0,
        earnings_per_share=4.0
    )
    
    print(f"\n📊 Dados de teste: {dados_teste.symbol}")
    print(f"   Preço: R$ {dados_teste.price}")
    print(f"   P/E: {dados_teste.pe_ratio}")
    print(f"   ROE: {dados_teste.roe}%")
    print(f"   Dividend Yield: {dados_teste.dividend_yield}%")
    
    # Teste 1: Análise Warren Buffett
    print("\n🎯 Teste 1: Análise Warren Buffett")
    try:
        resultado_buffett = AnaliseFinanceira.analise_warren_buffett(dados_teste)
        print(f"✅ Score: {resultado_buffett.score}/100")
        print(f"✅ Recomendação: {resultado_buffett.recomendacao}")
        print(f"✅ Pontos fortes: {len(resultado_buffett.pontos_fortes)}")
        print(f"✅ Pontos fracos: {len(resultado_buffett.pontos_fracos)}")
        if resultado_buffett.preco_alvo:
            print(f"✅ Preço alvo: R$ {resultado_buffett.preco_alvo:.2f}")
    except Exception as e:
        print(f"❌ Erro na análise Buffett: {e}")
    
    # Teste 2: Análise Benjamin Graham
    print("\n🛡️ Teste 2: Análise Benjamin Graham")
    try:
        resultado_graham = AnaliseFinanceira.analise_benjamin_graham(dados_teste)
        print(f"✅ Score: {resultado_graham.score}/100")
        print(f"✅ Recomendação: {resultado_graham.recomendacao}")
        if resultado_graham.margem_seguranca:
            print(f"✅ Margem de segurança: {resultado_graham.margem_seguranca:.1f}%")
    except Exception as e:
        print(f"❌ Erro na análise Graham: {e}")
    
    # Teste 3: Análise Peter Lynch
    print("\n📈 Teste 3: Análise Peter Lynch")
    try:
        resultado_lynch = AnaliseFinanceira.analise_peter_lynch(dados_teste)
        print(f"✅ Score: {resultado_lynch.score}/100")
        print(f"✅ Recomendação: {resultado_lynch.recomendacao}")
    except Exception as e:
        print(f"❌ Erro na análise Lynch: {e}")
    
    # Teste 4: Análise Dividendos
    print("\n💰 Teste 4: Análise Dividendos")
    try:
        resultado_dividendos = AnaliseFinanceira.analise_dividendos(dados_teste)
        print(f"✅ Score: {resultado_dividendos.score}/100")
        print(f"✅ Recomendação: {resultado_dividendos.recomendacao}")
    except Exception as e:
        print(f"❌ Erro na análise Dividendos: {e}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do Agente Investidor")
    print("=" * 50)
    
    # Testar APIs externas
    test_yahoo_finance_apis()
    test_worldbank_apis()
    
    # Testar análises internas
    test_analise_financeira()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main()

