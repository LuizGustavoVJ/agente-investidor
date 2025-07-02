from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

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
    
class MetodologiasInvestimento:
    """Classe que contém as metodologias dos 14 grandes investidores"""
    
    @staticmethod
    def get_perfis_investidores() -> Dict[str, PerfilInvestidor]:
        return {
            "warren_buffett": PerfilInvestidor(
                nome="Warren Buffett",
                tipo=TipoInvestidor.VALUE,
                metodologia="Value investing; foco em empresas sólidas, vantagem competitiva (moat), gestão de qualidade, geração de caixa e compra com margem de segurança",
                foco_principal="Empresas com vantagem competitiva sustentável",
                indicadores_chave=["P/E ratio", "ROE", "Debt/Equity", "Free Cash Flow", "Moat"],
                exemplos_investimentos=["Apple", "Coca-Cola", "Verisign", "GEICO", "BNSF Railway"],
                sites_recomendados=["marketscreener.com", "nordinvestimentos.com.br", "Berkshire Hathaway Annual Letters"],
                livros_recomendados=["The Intelligent Investor", "Essays of Warren Buffett"]
            ),
            
            "benjamin_graham": PerfilInvestidor(
                nome="Benjamin Graham",
                tipo=TipoInvestidor.VALUE,
                metodologia="Pai do value investing; foco em segurança de principal, análise fundamentalista, margem de segurança, empresas com dívida controlada",
                foco_principal="Segurança do principal e margem de segurança",
                indicadores_chave=["P/E ratio", "P/B ratio", "Debt/Equity", "Current Ratio", "Dividend Yield"],
                exemplos_investimentos=["GEICO"],
                sites_recomendados=["telesintese.com.br", "nordinvestimentos.com.br", "investidor10.com.br"],
                livros_recomendados=["Security Analysis", "The Intelligent Investor"]
            ),
            
            "george_soros": PerfilInvestidor(
                nome="George Soros",
                tipo=TipoInvestidor.MACRO,
                metodologia="Macro trading, teoria da reflexividade, aposta em tendências macroeconômicas e desequilíbrios globais",
                foco_principal="Tendências macroeconômicas globais",
                indicadores_chave=["Currency trends", "Interest rates", "Economic cycles", "Political events"],
                exemplos_investimentos=["British Pound short 1992"],
                sites_recomendados=["Bloomberg", "Reuters", "Financial Times"],
                livros_recomendados=["The Alchemy of Finance", "Soros on Soros"]
            ),
            
            "peter_lynch": PerfilInvestidor(
                nome="Peter Lynch",
                tipo=TipoInvestidor.GROWTH,
                metodologia="Investir em 'o que você conhece', analisar PEG ratio, focar em crescimento dentro de valor, small caps promissoras",
                foco_principal="Empresas em crescimento que você entende",
                indicadores_chave=["PEG ratio", "Earnings growth", "Revenue growth", "Market share"],
                exemplos_investimentos=["Dunkin' Donuts", "Taco Bell", "Chrysler"],
                sites_recomendados=["Morningstar", "Yahoo Finance"],
                livros_recomendados=["One Up On Wall Street", "Beating the Street"]
            ),
            
            "luiz_barsi": PerfilInvestidor(
                nome="Luiz Barsi Filho",
                tipo=TipoInvestidor.DIVIDEND,
                metodologia="Foco em geração de renda passiva, ações pagadoras de dividendos no mercado brasileiro, compra para longo prazo",
                foco_principal="Dividendos consistentes e crescentes",
                indicadores_chave=["Dividend Yield", "Payout Ratio", "Dividend Growth", "ROE", "Debt/Equity"],
                exemplos_investimentos=["Bancos brasileiros", "Utilities", "REITs"],
                sites_recomendados=["B3", "Fundamentus", "Status Invest"],
                livros_recomendados=["Ações que Pagam Dividendos"]
            ),
            
            "carl_icahn": PerfilInvestidor(
                nome="Carl Icahn",
                tipo=TipoInvestidor.ACTIVIST,
                metodologia="Activist investing - compra participação relevante para pressionar mudanças na gestão, estrutura de capital e valor",
                foco_principal="Empresas subvalorizadas com potencial de mudança",
                indicadores_chave=["Book Value", "Asset Value", "Management efficiency", "Corporate governance"],
                exemplos_investimentos=["Apple", "Netflix", "Herbalife"],
                sites_recomendados=["SEC filings", "Proxy statements"],
                livros_recomendados=["King Icahn"]
            ),
            
            "john_bogle": PerfilInvestidor(
                nome="John Bogle",
                tipo=TipoInvestidor.PASSIVE,
                metodologia="Fundo indexado, investimento passivo, minimização de taxas, foco em retorno de mercado a longo prazo",
                foco_principal="Diversificação de baixo custo",
                indicadores_chave=["Expense Ratio", "Tracking Error", "Market Beta"],
                exemplos_investimentos=["S&P 500 Index", "Total Stock Market Index"],
                sites_recomendados=["Vanguard", "Morningstar"],
                livros_recomendados=["Common Sense on Mutual Funds", "The Little Book of Common Sense Investing"]
            ),
            
            "geraldine_weiss": PerfilInvestidor(
                nome="Geraldine Weiss",
                tipo=TipoInvestidor.DIVIDEND,
                metodologia="Grande Dama dos Dividendos: dividend yield alto e consistente, foco no potencial de recuperação de preços",
                foco_principal="Dividendos altos com potencial de valorização",
                indicadores_chave=["Dividend Yield", "Dividend History", "Price recovery potential"],
                exemplos_investimentos=["Blue-chip dividend stocks"],
                sites_recomendados=["Dividend Detective"],
                livros_recomendados=["Dividends Don't Lie"]
            ),
            
            "seth_klarman": PerfilInvestidor(
                nome="Seth Klarman",
                tipo=TipoInvestidor.VALUE,
                metodologia="Deep value, margem de segurança extrema, investimento contra-cíclico, estratégia de risco/recompensa assimétrica",
                foco_principal="Situações especiais e deep value",
                indicadores_chave=["Margin of Safety", "Liquidation Value", "Special situations"],
                exemplos_investimentos=["Distressed securities", "Special situations"],
                sites_recomendados=["Baupost Group"],
                livros_recomendados=["Margin of Safety"]
            ),
            
            "linda_bradford_raschke": PerfilInvestidor(
                nome="Linda Bradford Raschke",
                tipo=TipoInvestidor.TECHNICAL,
                metodologia="Trading de curtíssimo prazo, swing trading e day trading, análise técnica, padrões de candlestick e volume",
                foco_principal="Padrões técnicos e momentum",
                indicadores_chave=["Moving Averages", "RSI", "Volume", "Candlestick patterns", "Support/Resistance"],
                exemplos_investimentos=["Futures", "Options", "Swing trades"],
                sites_recomendados=["TradingMarkets"],
                livros_recomendados=["Street Smarts"]
            ),
            
            "ray_dalio": PerfilInvestidor(
                nome="Ray Dalio",
                tipo=TipoInvestidor.MACRO,
                metodologia="Macro global, All Weather Portfolio, uso de correlações, ciclos de dívida, hedge e diversificação com risco balanceado",
                foco_principal="Diversificação global e gestão de risco",
                indicadores_chave=["Asset correlation", "Economic cycles", "Risk parity", "Global macro trends"],
                exemplos_investimentos=["Diversified global portfolio", "Commodities", "Bonds", "Currencies"],
                sites_recomendados=["Bridgewater Associates"],
                livros_recomendados=["Principles", "Big Debt Crises"]
            ),
            
            "jorge_paulo_lemann": PerfilInvestidor(
                nome="Jorge Paulo Lemann",
                tipo=TipoInvestidor.VALUE,
                metodologia="Foco em eficiência operacional, controle via 3G Capital, corte de custos e valor de longo prazo",
                foco_principal="Eficiência operacional e controle",
                indicadores_chave=["Operating Margin", "Cost reduction", "EBITDA growth", "Market share"],
                exemplos_investimentos=["Burger King", "Kraft Heinz", "AB InBev"],
                sites_recomendados=["3G Capital"],
                livros_recomendados=["Dream Big"]
            ),
            
            "lirio_parisotto": PerfilInvestidor(
                nome="Lírio Parisotto",
                tipo=TipoInvestidor.VALUE,
                metodologia="Investidor brasileiro com atuação em ações no Brasil e exterior, histórico de grandes lucros e perdas",
                foco_principal="Oportunidades de valor no Brasil",
                indicadores_chave=["P/E ratio", "P/B ratio", "Brazilian market dynamics"],
                exemplos_investimentos=["Ações brasileiras"],
                sites_recomendados=["B3", "CVM"],
                livros_recomendados=["Análise fundamentalista"]
            ),
            
            "victor_adler": PerfilInvestidor(
                nome="Victor Adler",
                tipo=TipoInvestidor.DIVIDEND,
                metodologia="Discrição, foco em dividendos, position trading de longo prazo no Brasil, participação relevante em empresas",
                foco_principal="Dividendos e posições de longo prazo",
                indicadores_chave=["Dividend Yield", "Long-term value", "Brazilian blue chips"],
                exemplos_investimentos=["Eternit", "Oi", "Eletrobras"],
                sites_recomendados=["cabotwealth.com", "validea.com", "aaii.com", "investidor10.com.br"],
                livros_recomendados=["Investimento em ações"]
            )
        }
    
    @staticmethod
    def get_metodologia_por_tipo(tipo: TipoInvestidor) -> List[PerfilInvestidor]:
        """Retorna todos os investidores de um tipo específico"""
        perfis = MetodologiasInvestimento.get_perfis_investidores()
        return [perfil for perfil in perfis.values() if perfil.tipo == tipo]
    
    @staticmethod
    def get_indicadores_por_tipo(tipo: TipoInvestidor) -> List[str]:
        """Retorna todos os indicadores únicos para um tipo de investimento"""
        perfis = MetodologiasInvestimento.get_metodologia_por_tipo(tipo)
        indicadores = set()
        for perfil in perfis:
            indicadores.update(perfil.indicadores_chave)
        return list(indicadores)

