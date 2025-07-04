"""
Módulo de dados e configurações para o Agente Investidor.

Este módulo contém constantes, configurações de APIs, dados de referência
e outras informações necessárias para o funcionamento do sistema.

Autor: Luiz Gustavo Finotello
Email: finotello22@hotmail.com
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# CONFIGURAÇÕES DE APIs
# =============================================================================

class APIConfig:
    """Configurações das APIs financeiras utilizadas."""
    
    # Yahoo Finance
    YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com"
    YAHOO_FINANCE_CHART_URL = f"{YAHOO_FINANCE_BASE_URL}/v8/finance/chart"
    YAHOO_FINANCE_QUOTE_URL = f"{YAHOO_FINANCE_BASE_URL}/v7/finance/quote"
    YAHOO_FINANCE_PROFILE_URL = f"{YAHOO_FINANCE_BASE_URL}/v10/finance/quoteSummary"
    
    # World Bank API
    WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"
    WORLD_BANK_INDICATORS_URL = f"{WORLD_BANK_BASE_URL}/indicator"
    
    # B3 (Bolsa do Brasil)
    B3_BASE_URL = "https://www.b3.com.br"
    B3_API_URL = f"{B3_BASE_URL}/api-portal"
    
    # Timeouts e configurações
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    CACHE_DURATION = 300  # 5 minutos

# =============================================================================
# DADOS DOS INVESTIDORES
# =============================================================================

@dataclass
class InvestorProfile:
    """Perfil de um investidor com suas características."""
    id: str
    nome: str
    tipo: str
    metodologia: str
    foco_principal: str
    indicadores_chave: List[str]
    criterios_pontuacao: Dict[str, Any]
    sites_recomendados: List[str]
    livros_recomendados: List[str]
    biografia_resumo: str

# Perfis dos investidores implementados
INVESTIDORES_PERFIS = {
    "warren_buffett": InvestorProfile(
        id="warren_buffett",
        nome="Warren Buffett",
        tipo="value",
        metodologia="Value Investing com foco em empresas com vantagem competitiva",
        foco_principal="Empresas com moats econômicos e gestão de qualidade",
        indicadores_chave=[
            "P/E < 25",
            "ROE > 15%",
            "D/E < 0.5",
            "Free Cash Flow positivo",
            "Crescimento consistente"
        ],
        criterios_pontuacao={
            "pe_ratio": {"ideal": 15, "max": 25, "peso": 20},
            "roe": {"min": 15, "ideal": 20, "peso": 25},
            "debt_to_equity": {"max": 0.5, "ideal": 0.3, "peso": 20},
            "free_cash_flow": {"min": 0, "peso": 20},
            "earnings_growth": {"min": 10, "peso": 15}
        },
        sites_recomendados=[
            "https://www.berkshirehathaway.com",
            "https://www.sec.gov/edgar",
            "https://www.morningstar.com"
        ],
        livros_recomendados=[
            "The Intelligent Investor - Benjamin Graham",
            "Security Analysis - Benjamin Graham",
            "The Essays of Warren Buffett - Warren Buffett"
        ],
        biografia_resumo="Warren Edward Buffett, conhecido como o 'Oráculo de Omaha', é um dos maiores investidores de todos os tempos. CEO da Berkshire Hathaway, é famoso por sua abordagem de value investing e por manter investimentos por décadas."
    ),
    
    "benjamin_graham": InvestorProfile(
        id="benjamin_graham",
        nome="Benjamin Graham",
        tipo="defensive_value",
        metodologia="Defensive Value com foco em margem de segurança",
        foco_principal="Segurança do principal e proteção contra perdas",
        indicadores_chave=[
            "P/E < 15",
            "P/B < 1.5",
            "Current Ratio > 2",
            "Margem de Segurança",
            "Dividendos consistentes"
        ],
        criterios_pontuacao={
            "pe_ratio": {"max": 15, "ideal": 10, "peso": 25},
            "pb_ratio": {"max": 1.5, "ideal": 1.0, "peso": 20},
            "current_ratio": {"min": 2.0, "ideal": 2.5, "peso": 20},
            "debt_to_equity": {"max": 0.5, "ideal": 0.3, "peso": 20},
            "dividend_yield": {"min": 2.0, "peso": 15}
        },
        sites_recomendados=[
            "https://www.sec.gov/edgar",
            "https://www.morningstar.com",
            "https://finance.yahoo.com"
        ],
        livros_recomendados=[
            "The Intelligent Investor - Benjamin Graham",
            "Security Analysis - Benjamin Graham",
            "The Interpretation of Financial Statements - Benjamin Graham"
        ],
        biografia_resumo="Benjamin Graham é considerado o 'Pai do Value Investing'. Professor da Columbia Business School e mentor de Warren Buffett, desenvolveu os fundamentos da análise de valores mobiliários."
    ),
    
    "peter_lynch": InvestorProfile(
        id="peter_lynch",
        nome="Peter Lynch",
        tipo="growth_at_reasonable_price",
        metodologia="Growth at Reasonable Price (GARP)",
        foco_principal="Crescimento a preço razoável em empresas conhecidas",
        indicadores_chave=[
            "PEG < 1",
            "Crescimento > 15%",
            "Empresas conhecidas",
            "Small/Mid Caps",
            "Inovação"
        ],
        criterios_pontuacao={
            "peg_ratio": {"max": 1.0, "ideal": 0.5, "peso": 30},
            "earnings_growth": {"min": 15, "ideal": 25, "peso": 25},
            "pe_ratio": {"max": 30, "ideal": 20, "peso": 20},
            "market_cap": {"preference": "small_mid", "peso": 15},
            "sector_familiarity": {"peso": 10}
        },
        sites_recomendados=[
            "https://www.fidelity.com",
            "https://www.morningstar.com",
            "https://finance.yahoo.com"
        ],
        livros_recomendados=[
            "One Up On Wall Street - Peter Lynch",
            "Beating the Street - Peter Lynch",
            "Learn to Earn - Peter Lynch"
        ],
        biografia_resumo="Peter Lynch gerenciou o Fidelity Magellan Fund de 1977 a 1990, obtendo retorno médio anual de 29.2%. Famoso pela filosofia 'invista no que você conhece' e pelo conceito de PEG ratio."
    ),
    
    "foco_dividendos": InvestorProfile(
        id="foco_dividendos",
        nome="Estratégia de Dividendos",
        tipo="income_investing",
        metodologia="Income Investing com foco em renda passiva",
        foco_principal="Geração de renda passiva através de dividendos crescentes",
        indicadores_chave=[
            "Dividend Yield > 4%",
            "Payout Ratio < 80%",
            "ROE > 12%",
            "Histórico consistente",
            "Crescimento de dividendos"
        ],
        criterios_pontuacao={
            "dividend_yield": {"min": 4.0, "ideal": 6.0, "peso": 30},
            "payout_ratio": {"max": 80, "ideal": 60, "peso": 25},
            "roe": {"min": 12, "ideal": 18, "peso": 20},
            "dividend_growth": {"min": 5, "peso": 15},
            "dividend_consistency": {"years": 5, "peso": 10}
        },
        sites_recomendados=[
            "https://www.dividendyieldhunter.com",
            "https://www.morningstar.com",
            "https://www.dividend.com"
        ],
        livros_recomendados=[
            "The Dividend Growth Investment Strategy - Roxann Klugman",
            "Dividends Don't Lie - Geraldine Weiss",
            "The Ultimate Dividend Playbook - Josh Peters"
        ],
        biografia_resumo="Estratégia baseada nos ensinamentos de investidores como Luiz Barsi Filho (Brasil) e Geraldine Weiss (EUA), focando na construção de renda passiva através de dividendos consistentes e crescentes."
    )
}

# =============================================================================
# SETORES E INDÚSTRIAS
# =============================================================================

class SetorEconomico(Enum):
    """Setores econômicos para classificação de empresas."""
    TECNOLOGIA = "technology"
    FINANCEIRO = "financial"
    SAUDE = "healthcare"
    ENERGIA = "energy"
    CONSUMO_BASICO = "consumer_staples"
    CONSUMO_DISCRICIONARIO = "consumer_discretionary"
    INDUSTRIAL = "industrial"
    MATERIAIS = "materials"
    TELECOMUNICACOES = "telecommunications"
    UTILITIES = "utilities"
    IMOBILIARIO = "real_estate"

# Mapeamento de setores para características
SETORES_CARACTERISTICAS = {
    SetorEconomico.TECNOLOGIA: {
        "volatilidade": "alta",
        "crescimento": "alto",
        "dividendos": "baixo",
        "ciclico": False,
        "defensivo": False
    },
    SetorEconomico.FINANCEIRO: {
        "volatilidade": "media",
        "crescimento": "medio",
        "dividendos": "medio",
        "ciclico": True,
        "defensivo": False
    },
    SetorEconomico.SAUDE: {
        "volatilidade": "baixa",
        "crescimento": "medio",
        "dividendos": "medio",
        "ciclico": False,
        "defensivo": True
    },
    SetorEconomico.ENERGIA: {
        "volatilidade": "alta",
        "crescimento": "baixo",
        "dividendos": "alto",
        "ciclico": True,
        "defensivo": False
    },
    SetorEconomico.CONSUMO_BASICO: {
        "volatilidade": "baixa",
        "crescimento": "baixo",
        "dividendos": "medio",
        "ciclico": False,
        "defensivo": True
    },
    SetorEconomico.UTILITIES: {
        "volatilidade": "baixa",
        "crescimento": "baixo",
        "dividendos": "alto",
        "ciclico": False,
        "defensivo": True
    }
}

# =============================================================================
# INDICADORES FINANCEIROS
# =============================================================================

@dataclass
class IndicadorFinanceiro:
    """Definição de um indicador financeiro."""
    nome: str
    formula: str
    descricao: str
    interpretacao: str
    faixa_ideal: Dict[str, float]
    categoria: str

# Dicionário de indicadores financeiros
INDICADORES_FINANCEIROS = {
    "pe_ratio": IndicadorFinanceiro(
        nome="P/E Ratio",
        formula="Preço por Ação / Lucro por Ação",
        descricao="Relação entre o preço da ação e o lucro por ação",
        interpretacao="Quanto menor, mais barata a ação em relação aos lucros",
        faixa_ideal={"min": 5, "max": 25, "ideal": 15},
        categoria="valuation"
    ),
    "pb_ratio": IndicadorFinanceiro(
        nome="P/B Ratio",
        formula="Preço por Ação / Valor Patrimonial por Ação",
        descricao="Relação entre o preço da ação e o valor contábil",
        interpretacao="Valores abaixo de 1 indicam ação negociada abaixo do valor contábil",
        faixa_ideal={"min": 0.5, "max": 2.0, "ideal": 1.0},
        categoria="valuation"
    ),
    "roe": IndicadorFinanceiro(
        nome="ROE",
        formula="Lucro Líquido / Patrimônio Líquido",
        descricao="Retorno sobre o patrimônio líquido",
        interpretacao="Mede a eficiência da empresa em gerar lucros com o capital dos acionistas",
        faixa_ideal={"min": 10, "max": 30, "ideal": 20},
        categoria="rentabilidade"
    ),
    "roa": IndicadorFinanceiro(
        nome="ROA",
        formula="Lucro Líquido / Ativos Totais",
        descricao="Retorno sobre os ativos",
        interpretacao="Mede a eficiência da empresa em gerar lucros com seus ativos",
        faixa_ideal={"min": 5, "max": 20, "ideal": 10},
        categoria="rentabilidade"
    ),
    "debt_to_equity": IndicadorFinanceiro(
        nome="D/E Ratio",
        formula="Dívida Total / Patrimônio Líquido",
        descricao="Relação entre dívida e patrimônio",
        interpretacao="Mede o nível de endividamento da empresa",
        faixa_ideal={"min": 0, "max": 1.0, "ideal": 0.3},
        categoria="endividamento"
    ),
    "current_ratio": IndicadorFinanceiro(
        nome="Liquidez Corrente",
        formula="Ativo Circulante / Passivo Circulante",
        descricao="Capacidade de pagamento de curto prazo",
        interpretacao="Valores acima de 1 indicam capacidade de honrar compromissos",
        faixa_ideal={"min": 1.0, "max": 3.0, "ideal": 2.0},
        categoria="liquidez"
    ),
    "dividend_yield": IndicadorFinanceiro(
        nome="Dividend Yield",
        formula="Dividendos por Ação / Preço por Ação",
        descricao="Rendimento de dividendos",
        interpretacao="Percentual de retorno em dividendos em relação ao preço da ação",
        faixa_ideal={"min": 2.0, "max": 10.0, "ideal": 5.0},
        categoria="dividendos"
    ),
    "peg_ratio": IndicadorFinanceiro(
        nome="PEG Ratio",
        formula="P/E Ratio / Taxa de Crescimento dos Lucros",
        descricao="P/E ajustado pelo crescimento",
        interpretacao="Valores abaixo de 1 indicam ação barata em relação ao crescimento",
        faixa_ideal={"min": 0.5, "max": 2.0, "ideal": 1.0},
        categoria="crescimento"
    )
}

# =============================================================================
# MENSAGENS E TEXTOS DO CHAT
# =============================================================================

CHAT_MENSAGENS = {
    "boas_vindas": "Olá! Sou seu agente investidor pessoal. Como posso ajudá-lo hoje?",
    "sugestoes": [
        "Como Warren Buffett analisa ações?",
        "O que é P/E ratio?",
        "Como começar a investir?",
        "Qual a diferença entre as metodologias?",
        "Como calcular o valor intrínseco de uma ação?"
    ],
    "erro_analise": "Desculpe, não foi possível analisar esta ação no momento. Verifique o símbolo e tente novamente.",
    "erro_dados": "Erro ao obter dados financeiros. Tente novamente em alguns instantes.",
    "processando": "Analisando ação... Por favor, aguarde."
}

# Respostas pré-definidas para o chat
CHAT_RESPOSTAS = {
    "warren_buffett": """Warren Buffett é conhecido como o "Oráculo de Omaha" e é um dos maiores investidores de todos os tempos. Sua metodologia se baseia em:

🎯 **Value Investing**: Comprar empresas por menos do que valem
📊 **Vantagem Competitiva**: Buscar empresas com "moats" econômicos
💰 **Margem de Segurança**: Comprar com desconto significativo
📈 **Longo Prazo**: Manter investimentos por décadas
🏢 **Gestão de Qualidade**: Empresas com líderes competentes

**Indicadores que Buffett valoriza:**
• P/E ratio razoável (< 25)
• ROE alto (> 15%)
• Dívida controlada (D/E < 0.5)
• Free Cash Flow positivo
• Crescimento consistente de lucros

Quer que eu analise alguma ação usando os critérios do Buffett?""",
    
    "pe_ratio": """O **P/E Ratio** (Price-to-Earnings) é um dos indicadores mais importantes para avaliar se uma ação está cara ou barata.

📊 **Fórmula**: Preço da Ação ÷ Lucro por Ação

**Como interpretar:**
• P/E baixo (< 15): Ação pode estar barata
• P/E médio (15-25): Preço justo
• P/E alto (> 25): Ação pode estar cara

**Exemplo prático:**
Se uma ação custa R$ 30 e a empresa lucra R$ 2 por ação:
P/E = 30 ÷ 2 = 15

Isso significa que você está pagando 15 vezes o lucro anual da empresa.

**Cuidados:**
• Compare com empresas do mesmo setor
• Considere o crescimento esperado
• Lucros negativos tornam o P/E inválido

Gostaria de saber sobre outros indicadores?""",
    
    "como_comecar": """Excelente pergunta! Aqui está um guia para começar a investir:

**1. 📚 Educação Financeira**
• Aprenda sobre diferentes tipos de investimento
• Entenda conceitos básicos (risco, retorno, diversificação)
• Estude as metodologias dos grandes investidores

**2. 💰 Organize suas Finanças**
• Quite dívidas de alto custo (cartão, cheque especial)
• Monte uma reserva de emergência (6-12 meses de gastos)
• Defina seus objetivos financeiros

**3. 🎯 Defina seu Perfil**
• Conservador: Foco em segurança
• Moderado: Equilibrio entre risco e retorno
• Agressivo: Maior tolerância ao risco

**4. 🏦 Abra uma Conta**
• Escolha uma corretora confiável
• Compare taxas e serviços
• Transfira recursos para investir

**5. 📈 Comece Gradualmente**
• Inicie com valores pequenos
• Diversifique seus investimentos
• Mantenha disciplina e foco no longo prazo

Quer que eu explique algum desses pontos em mais detalhes?"""
}

# =============================================================================
# CONFIGURAÇÕES DO SISTEMA
# =============================================================================

class SystemConfig:
    """Configurações gerais do sistema."""
    
    # Versão do sistema
    VERSION = "1.0.0"
    
    # Configurações de cache
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 minutos
    
    # Configurações de logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurações de análise
    MIN_SCORE = 0
    MAX_SCORE = 100
    DEFAULT_SCORE = 50
    
    # Configurações de recomendação
    SCORE_COMPRA = 70
    SCORE_NEUTRO = 50
    SCORE_VENDA = 30

# =============================================================================
# DADOS DE TESTE E SIMULAÇÃO
# =============================================================================

# Dados simulados para quando as APIs não estão disponíveis
DADOS_SIMULADOS = {
    "PETR4.SA": {
        "symbol": "PETR4.SA",
        "shortName": "PETROBRAS PN",
        "longName": "Petróleo Brasileiro S.A. - Petrobras",
        "currency": "BRL",
        "regularMarketPrice": 31.46,
        "regularMarketChange": 0.85,
        "regularMarketChangePercent": 2.78,
        "marketCap": 409000000000,
        "trailingPE": 12.5,
        "priceToBook": 1.2,
        "returnOnEquity": 0.19,
        "debtToEquity": 0.26,
        "dividendYield": 0.055,
        "sector": "Energy",
        "industry": "Oil & Gas Integrated"
    },
    "VALE3.SA": {
        "symbol": "VALE3.SA",
        "shortName": "VALE ON",
        "longName": "Vale S.A.",
        "currency": "BRL",
        "regularMarketPrice": 65.20,
        "regularMarketChange": -1.30,
        "regularMarketChangePercent": -1.95,
        "marketCap": 315000000000,
        "trailingPE": 8.9,
        "priceToBook": 1.8,
        "returnOnEquity": 0.22,
        "debtToEquity": 0.35,
        "dividendYield": 0.08,
        "sector": "Basic Materials",
        "industry": "Steel"
    },
    "AAPL": {
        "symbol": "AAPL",
        "shortName": "Apple Inc.",
        "longName": "Apple Inc.",
        "currency": "USD",
        "regularMarketPrice": 175.50,
        "regularMarketChange": 2.10,
        "regularMarketChangePercent": 1.21,
        "marketCap": 2750000000000,
        "trailingPE": 28.5,
        "priceToBook": 45.2,
        "returnOnEquity": 1.56,
        "debtToEquity": 1.73,
        "dividendYield": 0.005,
        "sector": "Technology",
        "industry": "Consumer Electronics"
    }
}

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_investor_profile(investor_id: str) -> InvestorProfile:
    """Retorna o perfil de um investidor pelo ID."""
    return INVESTIDORES_PERFIS.get(investor_id)

def get_all_investors() -> Dict[str, InvestorProfile]:
    """Retorna todos os perfis de investidores."""
    return INVESTIDORES_PERFIS

def get_indicator_info(indicator_name: str) -> IndicadorFinanceiro:
    """Retorna informações sobre um indicador financeiro."""
    return INDICADORES_FINANCEIROS.get(indicator_name)

def get_simulated_data(symbol: str) -> Dict[str, Any]:
    """Retorna dados simulados para um símbolo."""
    return DADOS_SIMULADOS.get(symbol.upper())

def is_brazilian_stock(symbol: str) -> bool:
    """Verifica se é uma ação brasileira."""
    return symbol.endswith('.SA')

def format_currency(value: float, currency: str = "BRL") -> str:
    """Formata um valor monetário."""
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif currency == "USD":
        return f"$ {value:,.2f}"
    else:
        return f"{value:,.2f} {currency}"

def calculate_score_range(score: int) -> str:
    """Retorna a classificação baseada no score."""
    if score >= SystemConfig.SCORE_COMPRA:
        return "COMPRA"
    elif score >= SystemConfig.SCORE_NEUTRO:
        return "NEUTRO"
    else:
        return "VENDA"

# =============================================================================
# CONSTANTES ADICIONAIS
# =============================================================================

# Sufixos de mercado
MARKET_SUFFIXES = {
    "BR": ".SA",  # Brasil
    "US": "",     # Estados Unidos
    "UK": ".L",   # Londres
    "CA": ".TO",  # Toronto
    "DE": ".DE",  # Alemanha
    "FR": ".PA",  # Paris
}

# Moedas por mercado
MARKET_CURRENCIES = {
    "BR": "BRL",
    "US": "USD",
    "UK": "GBP",
    "CA": "CAD",
    "DE": "EUR",
    "FR": "EUR",
}

# Horários de funcionamento dos mercados (UTC)
MARKET_HOURS = {
    "BR": {"open": "12:00", "close": "21:00"},  # B3
    "US": {"open": "14:30", "close": "21:00"},  # NYSE/NASDAQ
    "UK": {"open": "08:00", "close": "16:30"},  # LSE
}

if __name__ == "__main__":
    # Teste básico do módulo
    print(f"Agente Investidor Data Module v{SystemConfig.VERSION}")
    print(f"Investidores disponíveis: {len(INVESTIDORES_PERFIS)}")
    print(f"Indicadores financeiros: {len(INDICADORES_FINANCEIROS)}")
    print(f"Dados simulados: {len(DADOS_SIMULADOS)}")

