from dataclasses import dataclass
from typing import List
from enum import Enum
from .metodologias import (
    ValueInvesting, GrowthInvesting, DividendInvesting, TechnicalTrading,
    MacroTrading, ActivistInvesting, PassiveInvesting, DefensiveValue,
    GrowthAtReasonablePrice, IncomeInvesting, VictorAdlerInvesting,
    AllWeatherPortfolio, OperationalExcellence, AggressiveInvesting,
    LuizBarsiFilhoInvesting
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
    ValueInvesting,              # Warren Buffett
    GrowthInvesting,             # Peter Lynch, Seth Klarman
    DividendInvesting,           # Geraldine Weiss
    LuizBarsiFilhoInvesting,     # Luiz Barsi Filho
    TechnicalTrading,            # Linda Bradford Raschke
    MacroTrading,                # George Soros
    ActivistInvesting,           # Carl Icahn
    PassiveInvesting,            # John Bogle
    DefensiveValue,              # Benjamin Graham
    GrowthAtReasonablePrice,     # Peter Lynch
    IncomeInvesting,             # Luiz Barsi Filho (genérica)
    VictorAdlerInvesting,        # Victor Adler
    AllWeatherPortfolio,         # Ray Dalio
    OperationalExcellence,       # Jorge Paulo Lemann
    AggressiveInvesting,         # Lírio Parisotto
]

METODOLOGIAS_MAP = {m.nome: m for m in METODOLOGIAS}

# Mapeamento de metodologias recomendadas por perfil
METODOLOGIAS_POR_PERFIL = {
    'conservador': [
        {
            'nome': 'Benjamin Graham',
            'classe': DefensiveValue,
            'descricao': (
                'Foco em segurança de principal, empresas com dívida controlada '
                'e margem de segurança. Ideal para iniciantes e quem busca '
                'estabilidade.'
            )
        },
        {
            'nome': 'John Bogle',
            'classe': PassiveInvesting,
            'descricao': (
                'Investimento passivo em fundos indexados, minimizando riscos e '
                'taxas. Estratégia de longo prazo com pouca necessidade de '
                'acompanhamento.'
            )
        },
        {
            'nome': 'Geraldine Weiss',
            'classe': DividendInvesting,
            'descricao': (
                'Estratégia de dividendos consistentes, ideal para geração de '
                'renda passiva com menor volatilidade.'
            )
        },
        {
            'nome': 'Luiz Barsi Filho',
            'classe': IncomeInvesting,
            'descricao': (
                'Ações brasileiras pagadoras de dividendos com foco no longo '
                'prazo. Estratégia simples e eficaz para renda previsível.'
            )
        },
        {
            'nome': 'Victor Adler',
            'classe': DividendInvesting,
            'descricao': (
                'Abordagem discreta e focada em dividendos, alinhada com perfil '
                'conservador.'
            )
        },
    ],
    'moderado': [
        {
            'nome': 'Warren Buffett',
            'classe': ValueInvesting,
            'descricao': (
                'Value investing com foco em empresas sólidas e margens de '
                'segurança. Ideal para investidores que aceitam volatilidade '
                'moderada.'
            )
        },
        {
            'nome': 'Peter Lynch',
            'classe': GrowthAtReasonablePrice,
            'descricao': (
                'Investir em empresas conhecidas, com potencial de crescimento e '
                'bom histórico. Combina análise fundamentalista com crescimento.'
            )
        },
        {
            'nome': 'Ray Dalio',
            'classe': MacroTrading,
            'descricao': (
                '“All Weather Portfolio” com diversificação balanceada de risco. '
                'Estratégia robusta para diferentes cenários econômicos.'
            )
        },
        {
            'nome': 'Seth Klarman',
            'classe': GrowthInvesting,
            'descricao': (
                'Deep value com margem de segurança elevada. Exige um pouco mais '
                'de conhecimento, mas ainda pode ser moderadamente seguro.'
            )
        },
        {
            'nome': 'Jorge Paulo Lemann',
            'classe': ActivistInvesting,
            'descricao': (
                'Investimentos em eficiência operacional e geração de valor no '
                'longo prazo. Boa opção para moderados com apetite para empresas '
                'líderes.'
            )
        },
    ],
    'arrojado': [
        {
            'nome': 'George Soros',
            'classe': MacroTrading,
            'descricao': (
                'Macro trading e reflexividade. Estratégia de alta complexidade e '
                'risco, com foco em grandes tendências globais.'
            )
        },
        {
            'nome': 'Carl Icahn',
            'classe': ActivistInvesting,
            'descricao': (
                'Activist investing: exige grande conhecimento e capacidade de '
                'influência. Alta exposição, mas com potencial elevado.'
            )
        },
        {
            'nome': 'Linda Bradford Raschke',
            'classe': TechnicalTrading,
            'descricao': (
                'Day-trading e swing trading com análise técnica. Alta frequência '
                'e risco, exige habilidade técnica e sangue-frio.'
            )
        },
        {
            'nome': 'Seth Klarman',
            'classe': GrowthInvesting,
            'descricao': (
                'Estratégias contrárias e assimétricas, aproveitando pânico ou '
                'oportunidades negligenciadas.'
            )
        },
        {
            'nome': 'Lírio Parisotto',
            'classe': GrowthInvesting,
            'descricao': (
                'Investimentos agressivos, com histórico de grandes ganhos e '
                'perdas. Alta exposição, estratégia não padronizada.'
            )
        },
    ]
}

