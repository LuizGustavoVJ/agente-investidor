from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import requests
import json
from datetime import datetime

from src.models.investidor import MetodologiasInvestimento, TipoInvestidor
from src.models.analise_financeira import AnaliseFinanceira, DadosFinanceiros, AnaliseResultado
from src.data import (
    INVESTIDORES_PERFIS, 
    CHAT_MENSAGENS, 
    CHAT_RESPOSTAS, 
    APIConfig,
    get_simulated_data,
    is_brazilian_stock,
    format_currency,
    calculate_score_range,
    get_all_investors
)

agente_bp = Blueprint('agente', __name__)

@agente_bp.route('/perfis-investidores', methods=['GET'])
@cross_origin()
def get_perfis_investidores():
    """Retorna todos os perfis de investidores disponíveis"""
    try:
        perfis = get_all_investors()
        perfis_dict = {}
        
        for key, perfil in perfis.items():
            perfis_dict[key] = {
                'nome': perfil.nome,
                'tipo': perfil.tipo,
                'metodologia': perfil.metodologia,
                'foco_principal': perfil.foco_principal,
                'indicadores_chave': perfil.indicadores_chave,
                'sites_recomendados': perfil.sites_recomendados,
                'livros_recomendados': perfil.livros_recomendados,
                'biografia_resumo': perfil.biografia_resumo
            }
        
        return jsonify({
            'success': True,
            'data': perfis_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agente_bp.route('/tipos-investimento', methods=['GET'])
@cross_origin()
def get_tipos_investimento():
    """Retorna os tipos de investimento disponíveis"""
    try:
        tipos = [tipo.value for tipo in TipoInvestidor]
        return jsonify({
            'success': True,
            'data': tipos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agente_bp.route('/indicadores-por-tipo/<tipo>', methods=['GET'])
@cross_origin()
def get_indicadores_por_tipo(tipo):
    """Retorna indicadores específicos para um tipo de investimento"""
    try:
        tipo_enum = TipoInvestidor(tipo)
        indicadores = MetodologiasInvestimento.get_indicadores_por_tipo(tipo_enum)
        
        return jsonify({
            'success': True,
            'data': {
                'tipo': tipo,
                'indicadores': indicadores
            }
        })
    except ValueError:
        return jsonify({
            'success': False,
            'error': f'Tipo de investimento inválido: {tipo}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agente_bp.route('/dados-acao/<symbol>', methods=['GET'])
@cross_origin()
def get_dados_acao(symbol):
    """Obtém dados de uma ação usando as APIs financeiras"""
    try:
        # Determinar região baseada no símbolo
        region = 'BR' if '.SA' in symbol.upper() else 'US'
        
        # Tentar obter dados reais da API do Yahoo Finance
        try:
            url = f"{APIConfig.YAHOO_FINANCE_CHART_URL}/{symbol.upper()}"
            params = {
                'interval': '1d',
                'range': '1y',
                'events': 'div,split'
            }
            
            response = requests.get(url, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('chart') and data['chart'].get('result'):
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    # Processar dados
                    dados_processados = {
                        'symbol': symbol.upper(),
                        'profile': {
                            'shortName': meta.get('symbol', symbol),
                            'longName': meta.get('longName', symbol),
                            'currency': meta.get('currency', 'USD'),
                            'regularMarketPrice': meta.get('regularMarketPrice'),
                            'regularMarketChange': meta.get('regularMarketChange'),
                            'regularMarketChangePercent': meta.get('regularMarketChangePercent'),
                            'marketCap': meta.get('marketCap'),
                            'sector': meta.get('sector'),
                            'industry': meta.get('industry')
                        },
                        'chart': result,
                        'insights': None,
                        'region': region
                    }
                    
                    return jsonify({
                        'success': True,
                        'data': dados_processados
                    })
            
            # Se chegou aqui, a API não retornou dados válidos
            raise Exception("API não retornou dados válidos")
            
        except Exception as api_error:
            # Fallback para dados simulados
            dados_simulados = get_simulated_data(symbol.upper())
            
            if dados_simulados:
                dados_processados = {
                    'symbol': symbol.upper(),
                    'profile': dados_simulados,
                    'chart': None,
                    'insights': None,
                    'region': region,
                    'simulated': True
                }
                
                return jsonify({
                    'success': True,
                    'data': dados_processados
                })
            else:
                raise Exception(f"Símbolo não encontrado: {symbol}")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agente_bp.route('/analisar-acao', methods=['POST'])
@cross_origin()
def analisar_acao():
    """Analisa uma ação usando as metodologias dos grandes investidores"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        metodologia = data.get('metodologia', 'warren_buffett')
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Símbolo da ação é obrigatório'
            }), 400
        
        # Obter dados da ação
        region = 'BR' if '.SA' in symbol else 'US'
        
        try:
            # Tentar obter dados reais da API do Yahoo Finance
            url = f"{APIConfig.YAHOO_FINANCE_CHART_URL}/{symbol}"
            params = {
                'interval': '1d',
                'range': '1mo'
            }
            
            response = requests.get(url, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
            
            price = None
            market_cap = None
            
            if response.status_code == 200:
                chart_data = response.json()
                
                if chart_data.get('chart') and chart_data['chart'].get('result'):
                    result = chart_data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    # Extrair dados básicos
                    price = meta.get('regularMarketPrice', 0)
                    market_cap = meta.get('marketCap')
            
            # Se não conseguiu obter dados da API, usar dados simulados
            if price is None:
                dados_simulados = get_simulated_data(symbol)
                if dados_simulados:
                    price = dados_simulados.get('regularMarketPrice', 0)
                    market_cap = dados_simulados.get('marketCap', 0)
                else:
                    # Usar valores padrão para demonstração
                    price = 100.0
                    market_cap = 1000000000
            
            # Criar objeto DadosFinanceiros com dados disponíveis
            # Para demonstração, vamos usar alguns valores padrão baseados no símbolo
            # Em produção, estes dados viriam de APIs mais completas
            
            # Valores padrão baseados em dados típicos do mercado
            if symbol.endswith('.SA'):  # Ações brasileiras
                pe_default = 12.0
                pb_default = 1.5
                roe_default = 15.0
                dividend_yield_default = 5.0
            else:  # Ações americanas
                pe_default = 20.0
                pb_default = 3.0
                roe_default = 18.0
                dividend_yield_default = 2.0
            
            dados_financeiros = DadosFinanceiros(
                symbol=symbol,
                price=price,
                market_cap=market_cap or 1000000000,
                pe_ratio=data.get('pe_ratio', pe_default),
                pb_ratio=data.get('pb_ratio', pb_default),
                peg_ratio=data.get('peg_ratio', 1.2),
                dividend_yield=data.get('dividend_yield', dividend_yield_default),
                roe=data.get('roe', roe_default),
                roa=data.get('roa', 8.0),
                debt_to_equity=data.get('debt_to_equity', 0.4),
                current_ratio=data.get('current_ratio', 1.8),
                free_cash_flow=data.get('free_cash_flow', 100000000),
                revenue_growth=data.get('revenue_growth', 10.0),
                earnings_growth=data.get('earnings_growth', 12.0),
                profit_margin=data.get('profit_margin', 15.0),
                operating_margin=data.get('operating_margin', 20.0),
                book_value_per_share=data.get('book_value_per_share', price / pb_default),
                earnings_per_share=data.get('earnings_per_share', price / pe_default)
            )
            
            # Aplicar metodologia de análise
            if metodologia == 'warren_buffett':
                resultado = AnaliseFinanceira.analise_warren_buffett(dados_financeiros)
            elif metodologia == 'benjamin_graham':
                resultado = AnaliseFinanceira.analise_benjamin_graham(dados_financeiros)
            elif metodologia == 'peter_lynch':
                resultado = AnaliseFinanceira.analise_peter_lynch(dados_financeiros)
            elif metodologia == 'foco_dividendos':
                resultado = AnaliseFinanceira.analise_dividendos(dados_financeiros)
            else:
                return jsonify({
                    'success': False,
                    'error': f'Metodologia não suportada: {metodologia}'
                }), 400
            
            # Converter resultado para dict
            resultado_dict = {
                'symbol': resultado.symbol,
                'score': resultado.score,
                'recomendacao': resultado.recomendacao,
                'metodologia_aplicada': resultado.metodologia_aplicada,
                'pontos_fortes': resultado.pontos_fortes,
                'pontos_fracos': resultado.pontos_fracos,
                'preco_alvo': resultado.preco_alvo,
                'margem_seguranca': resultado.margem_seguranca,
                'justificativa': resultado.justificativa,
                'preco_atual': price,
                'dados_utilizados': {
                    'pe_ratio': dados_financeiros.pe_ratio,
                    'pb_ratio': dados_financeiros.pb_ratio,
                    'peg_ratio': dados_financeiros.peg_ratio,
                    'dividend_yield': dados_financeiros.dividend_yield,
                    'roe': dados_financeiros.roe,
                    'debt_to_equity': dados_financeiros.debt_to_equity
                }
            }
            
            return jsonify({
                'success': True,
                'data': resultado_dict
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro ao analisar ação: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agente_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat_agente():
    """Chat com o agente investidor"""
    try:
        data = request.json
        mensagem = data.get('mensagem', '')
        contexto = data.get('contexto', {})
        
        if not mensagem:
            return jsonify({
                'success': False,
                'error': 'Mensagem é obrigatória'
            }), 400
        
        # Processar mensagem e gerar resposta
        resposta = processar_mensagem_chat(mensagem, contexto)
        
        return jsonify({
            'success': True,
            'data': {
                'resposta': resposta,
                'timestamp': str(datetime.now())
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agente_bp.route('/recomendacoes-mercado', methods=['GET'])
@cross_origin()
def get_recomendacoes_mercado():
    """Obtém recomendações gerais do mercado"""
    try:
        # Lista de ações brasileiras populares para análise
        acoes_populares = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA']
        recomendacoes = []
        
        for symbol in acoes_populares:
            try:
                # Tentar obter dados reais da API
                url = f"{APIConfig.YAHOO_FINANCE_CHART_URL}/{symbol}"
                params = {
                    'interval': '1d',
                    'range': '1mo'
                }
                
                response = requests.get(url, params=params, timeout=APIConfig.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    chart_data = response.json()
                    
                    if chart_data.get('chart') and chart_data['chart'].get('result'):
                        result = chart_data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        # Calcular variação recente
                        timestamps = result.get('timestamp', [])
                        quotes = result.get('indicators', {}).get('quote', [{}])[0]
                        closes = quotes.get('close', [])
                        
                        if len(closes) >= 2:
                            variacao = ((closes[-1] - closes[0]) / closes[0]) * 100
                            
                            recomendacoes.append({
                                'symbol': symbol,
                                'nome': meta.get('longName', symbol),
                                'preco_atual': meta.get('regularMarketPrice'),
                                'variacao_periodo': round(variacao, 2),
                                'volume': meta.get('regularMarketVolume'),
                                'status': 'alta' if variacao > 5 else 'baixa' if variacao < -5 else 'estavel'
                            })
                        continue
                
                # Fallback para dados simulados se API falhar
                dados_simulados = get_simulated_data(symbol)
                if dados_simulados:
                    # Simular variação aleatória para demonstração
                    import random
                    variacao = random.uniform(-10, 10)
                    
                    recomendacoes.append({
                        'symbol': symbol,
                        'nome': dados_simulados.get('longName', symbol),
                        'preco_atual': dados_simulados.get('regularMarketPrice'),
                        'variacao_periodo': round(variacao, 2),
                        'volume': dados_simulados.get('regularMarketVolume', 1000000),
                        'status': 'alta' if variacao > 5 else 'baixa' if variacao < -5 else 'estavel'
                    })
                    
            except Exception as e:
                continue
        
        # Se não conseguiu obter nenhuma recomendação, usar dados simulados
        if not recomendacoes:
            import random
            for symbol in acoes_populares:
                dados_simulados = get_simulated_data(symbol)
                if dados_simulados:
                    variacao = random.uniform(-10, 10)
                    recomendacoes.append({
                        'symbol': symbol,
                        'nome': dados_simulados.get('longName', symbol),
                        'preco_atual': dados_simulados.get('regularMarketPrice'),
                        'variacao_periodo': round(variacao, 2),
                        'volume': dados_simulados.get('regularMarketVolume', 1000000),
                        'status': 'alta' if variacao > 5 else 'baixa' if variacao < -5 else 'estavel'
                    })
        
        return jsonify({
            'success': True,
            'data': {
                'recomendacoes': recomendacoes,
                'timestamp': str(datetime.now()),
                'mercado': 'Brasil - B3'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def processar_mensagem_chat(mensagem: str, contexto: dict) -> str:
    """Processa mensagem do chat e gera resposta do agente"""
    mensagem_lower = mensagem.lower()
    
    # Respostas baseadas em palavras-chave
    if any(palavra in mensagem_lower for palavra in ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
        return """Olá! Sou seu agente investidor pessoal, especializado nas metodologias dos maiores investidores do mundo como Warren Buffett, Benjamin Graham, Peter Lynch e outros.

Como posso ajudá-lo hoje? Posso:
• Analisar ações específicas
• Explicar metodologias de investimento
• Dar recomendações baseadas em diferentes estratégias
• Ensinar sobre indicadores financeiros

Digite o símbolo de uma ação (ex: PETR4.SA) ou faça uma pergunta sobre investimentos!"""
    
    elif any(palavra in mensagem_lower for palavra in ['warren buffett', 'buffett']):
        return """Warren Buffett é conhecido como o "Oráculo de Omaha" e é um dos maiores investidores de todos os tempos. Sua metodologia se baseia em:

🎯 **Value Investing**: Comprar empresas por menos do que valem
📊 **Vantagem Competitiva**: Buscar empresas com "moats" (fossos econômicos)
💰 **Margem de Segurança**: Comprar com desconto significativo
📈 **Longo Prazo**: Manter investimentos por décadas
🏢 **Gestão de Qualidade**: Empresas com líderes competentes

**Indicadores que Buffett valoriza:**
• P/E ratio razoável (< 25)
• ROE alto (> 15%)
• Dívida controlada (D/E < 0.5)
• Free Cash Flow positivo
• Crescimento consistente de lucros

Quer que eu analise alguma ação usando os critérios do Buffett?"""
    
    elif any(palavra in mensagem_lower for palavra in ['benjamin graham', 'graham']):
        return """Benjamin Graham é considerado o "Pai do Value Investing" e mentor de Warren Buffett. Sua abordagem é mais conservadora:

🛡️ **Segurança do Principal**: Proteção contra perdas é prioridade
📊 **Análise Fundamentalista**: Foco nos números da empresa
💎 **Margem de Segurança**: Comprar bem abaixo do valor intrínseco
⚖️ **Investidor Defensivo vs Empreendedor**: Diferentes estratégias para diferentes perfis

**Critérios de Graham:**
• P/E < 15
• P/B < 1.5
• Current Ratio > 2
• Debt/Equity < 0.5
• Histórico de dividendos

**Fórmula do Valor Intrínseco de Graham:**
V = √(22.5 × EPS × Book Value)

Gostaria de analisar uma ação usando os critérios conservadores de Graham?"""
    
    elif any(palavra in mensagem_lower for palavra in ['peter lynch', 'lynch']):
        return """Peter Lynch é famoso por sua filosofia "invista no que você conhece" e por ter batido o mercado por 13 anos consecutivos no Fidelity Magellan Fund.

🔍 **Invista no que Conhece**: Empresas cujos produtos/serviços você entende
📈 **Growth at Reasonable Price**: Crescimento a preço razoável
🎯 **PEG Ratio**: Indicador favorito (P/E ÷ Crescimento)
🏪 **Small Caps**: Foco em empresas menores com potencial

**Critérios de Lynch:**
• PEG Ratio < 1 (ideal)
• Crescimento de lucros > 15%
• Empresas que você entende
• Produtos/serviços em expansão
• Gestão competente

**Categorias de Ações segundo Lynch:**
• **Slow Growers**: Empresas maduras, crescimento lento
• **Stalwarts**: Blue chips, crescimento moderado
• **Fast Growers**: Alto crescimento (favoritas)
• **Cyclicals**: Dependem de ciclos econômicos
• **Turnarounds**: Empresas em recuperação
• **Asset Plays**: Valor nos ativos

Quer analisar uma ação usando a metodologia de Lynch?"""
    
    elif any(palavra in mensagem_lower for palavra in ['dividendos', 'dividend', 'barsi', 'renda passiva']):
        return """Investimento em dividendos é uma estratégia focada em renda passiva, popularizada no Brasil por Luiz Barsi Filho e internacionalmente por Geraldine Weiss.

💰 **Foco em Renda**: Receber dividendos regulares
📊 **Dividend Yield**: Percentual de dividendos sobre o preço
🔄 **Reinvestimento**: Usar dividendos para comprar mais ações
⏰ **Longo Prazo**: Estratégia de "buy and hold"

**Critérios para Ações de Dividendos:**
• Dividend Yield > 4%
• Payout Ratio < 80% (sustentabilidade)
• ROE > 12% (capacidade de gerar lucro)
• Histórico consistente de pagamentos
• Dívida controlada
• Setor defensivo (utilities, bancos, consumo)

**Vantagens:**
✅ Renda passiva regular
✅ Proteção contra inflação
✅ Empresas maduras e estáveis
✅ Disciplina de investimento

**Cuidados:**
⚠️ Yield muito alto pode indicar problemas
⚠️ Cortes de dividendos são possíveis
⚠️ Tributação sobre dividendos

Quer que eu analise ações com foco em dividendos?"""
    
    elif any(palavra in mensagem_lower for palavra in ['análise técnica', 'gráfico', 'candlestick']):
        return """A análise técnica estuda padrões de preços e volume para prever movimentos futuros, muito usada por traders como Linda Bradford Raschke.

📊 **Gráficos**: Candlesticks, barras, linhas
📈 **Tendências**: Identificar direção do mercado
🎯 **Suporte e Resistência**: Níveis importantes de preço
📉 **Indicadores**: RSI, MACD, Médias Móveis

**Principais Indicadores:**
• **Médias Móveis**: Tendência de longo prazo
• **RSI**: Sobrecompra/sobrevenda (0-100)
• **MACD**: Convergência/divergência de médias
• **Volume**: Confirma movimentos de preço
• **Bollinger Bands**: Volatilidade

**Padrões de Candlestick:**
• Doji: Indecisão
• Hammer: Possível reversão de alta
• Shooting Star: Possível reversão de baixa
• Engulfing: Padrão de reversão

**Timeframes:**
• Day Trading: 1m, 5m, 15m
• Swing Trading: 1h, 4h, 1d
• Position Trading: 1d, 1w, 1m

Nota: Combino análise técnica com fundamentalista para decisões mais robustas!"""
    
    elif any(palavra in mensagem_lower for palavra in ['p/e', 'pe ratio', 'preço lucro']):
        return """O P/E Ratio (Price-to-Earnings) é um dos indicadores mais importantes para avaliar se uma ação está cara ou barata.

📊 **Fórmula**: P/E = Preço da Ação ÷ Lucro por Ação (LPA)

**Interpretação:**
• **P/E Baixo (< 15)**: Ação potencialmente barata
• **P/E Moderado (15-25)**: Preço razoável
• **P/E Alto (> 25)**: Ação potencialmente cara

**Variações:**
• **P/E Trailing**: Baseado nos últimos 12 meses
• **P/E Forward**: Baseado em projeções futuras
• **P/E Ajustado**: Considerando itens extraordinários

**Cuidados:**
⚠️ P/E muito baixo pode indicar problemas
⚠️ Comparar com empresas do mesmo setor
⚠️ Considerar crescimento (PEG Ratio)
⚠️ Lucros podem ser manipulados

**Benchmarks por Setor:**
• Bancos: 8-15
• Utilities: 12-18
• Tecnologia: 20-35
• Crescimento: 25-50

**Exemplo:**
Ação a R$ 50, LPA = R$ 5
P/E = 50 ÷ 5 = 10x
(Investidor paga 10x o lucro anual)

Quer que eu calcule o P/E de alguma ação específica?"""
    
    elif any(palavra in mensagem_lower for palavra in ['roe', 'return on equity', 'retorno patrimônio']):
        return """ROE (Return on Equity) mede a eficiência da empresa em gerar lucro com o patrimônio dos acionistas.

📊 **Fórmula**: ROE = Lucro Líquido ÷ Patrimônio Líquido × 100

**Interpretação:**
• **ROE > 20%**: Excelente
• **ROE 15-20%**: Muito bom
• **ROE 10-15%**: Bom
• **ROE < 10%**: Fraco

**Por que é Importante:**
✅ Mostra eficiência da gestão
✅ Indica capacidade de crescimento
✅ Favorito de Warren Buffett
✅ Permite comparação entre empresas

**Decomposição DuPont:**
ROE = Margem Líquida × Giro do Ativo × Multiplicador de Equity

**Cuidados:**
⚠️ ROE muito alto pode indicar alavancagem excessiva
⚠️ Comparar com empresas do mesmo setor
⚠️ Verificar consistência ao longo do tempo
⚠️ Considerar qualidade dos lucros

**Benchmarks por Setor:**
• Bancos: 12-18%
• Varejo: 15-25%
• Tecnologia: 15-30%
• Utilities: 8-12%

**Exemplo:**
Lucro: R$ 100 milhões
Patrimônio: R$ 500 milhões
ROE = 100 ÷ 500 × 100 = 20%

Warren Buffett busca empresas com ROE consistentemente > 15%!"""
    
    elif any(palavra in mensagem_lower for palavra in ['como começar', 'iniciante', 'começar investir']):
        return """Bem-vindo ao mundo dos investimentos! Aqui está um guia para começar:

🎯 **1. Defina seus Objetivos**
• Aposentadoria
• Compra de imóvel
• Reserva de emergência
• Renda extra

📚 **2. Educação Financeira**
• Leia "O Investidor Inteligente" (Benjamin Graham)
• Estude sobre risco e retorno
• Entenda diferentes tipos de investimento

💰 **3. Organize suas Finanças**
• Quite dívidas de cartão de crédito
• Monte reserva de emergência (6-12 meses)
• Defina quanto pode investir mensalmente

📊 **4. Comece Simples**
• Tesouro Direto (renda fixa)
• Fundos de índice (diversificação)
• Ações de empresas que você conhece

🎓 **5. Metodologias para Estudar**
• **Warren Buffett**: Value investing, longo prazo
• **Benjamin Graham**: Segurança e margem de segurança
• **Peter Lynch**: Invista no que conhece
• **Luiz Barsi**: Foco em dividendos

⚠️ **Erros Comuns a Evitar**
• Investir sem conhecimento
• Seguir dicas de "gurus"
• Tentar timing do mercado
• Não diversificar
• Investir dinheiro que precisa no curto prazo

Quer que eu explique alguma metodologia específica ou analise uma ação para você começar?"""
    
    # Verificar se é um símbolo de ação
    elif any(char.isalpha() for char in mensagem) and len(mensagem.strip()) <= 10:
        symbol = mensagem.strip().upper()
        return f"""Vou analisar a ação {symbol} para você!

Para uma análise completa, preciso que você escolha uma metodologia:

🎯 **Warren Buffett** - Value investing, empresas com vantagem competitiva
📊 **Benjamin Graham** - Análise defensiva, margem de segurança
📈 **Peter Lynch** - Crescimento a preço razoável (PEG < 1)
💰 **Foco em Dividendos** - Renda passiva, dividend yield

Use o botão "Analisar Ação" na interface ou me diga qual metodologia prefere!

Também posso explicar:
• Como calcular indicadores (P/E, ROE, etc.)
• Estratégias de cada investidor
• Análise do setor da empresa
• Comparação com concorrentes

O que gostaria de saber sobre {symbol}?"""
    
    else:
        return """Não entendi sua pergunta, mas posso ajudar com:

📊 **Análise de Ações**
• Digite o símbolo (ex: PETR4.SA, AAPL)
• Análise fundamentalista
• Recomendações baseadas em grandes investidores

🎓 **Educação Financeira**
• Metodologias de investimento
• Indicadores financeiros (P/E, ROE, etc.)
• Estratégias de longo prazo

💡 **Perguntas que posso responder:**
• "Como Warren Buffett analisa ações?"
• "O que é P/E ratio?"
• "Como começar a investir?"
• "Explique sobre dividendos"

🔍 **Análise de Mercado**
• Recomendações atuais
• Tendências do mercado brasileiro
• Comparação de setores

Digite sua pergunta ou o símbolo de uma ação que quer analisar!"""

from datetime import datetime

