from .value_investing import ValueInvesting
from .defensive_value import DefensiveValue
from .growth_at_reasonable_price import GrowthAtReasonablePrice
from .dividend_investing import DividendInvesting, VictorAdlerInvesting, LuizBarsiFilhoInvesting
from .income_investing import IncomeInvesting
from .passive_investing import PassiveInvesting
from .macro_trading import MacroTrading, AllWeatherPortfolio
from .activist_investing import ActivistInvesting, OperationalExcellence
from .technical_trading import TechnicalTrading
from .growth_investing import GrowthInvesting, AggressiveInvesting

# Importações explícitas das metodologias dos grandes investidores
# (nomes das classes conforme implementado nos arquivos)
# John Bogle = PassiveInvesting (já importado)
# Geraldine Weiss = DividendInvesting (já importado)
# Luiz Barsi Filho = DividendInvesting (já importado)
# Victor Adler = VictorAdlerInvesting (já importado)
# Ray Dalio = AllWeatherPortfolio (já importado)
# Seth Klarman = GrowthInvesting (já importado)
# Jorge Paulo Lemann = OperationalExcellence (já importado)
# George Soros = MacroTrading (já importado)
# Carl Icahn = ActivistInvesting (já importado)
# Linda Bradford Raschke = TechnicalTrading (já importado)
# Lírio Parisotto = AggressiveInvesting (já importado)

__all__ = [
    "ValueInvesting",
    "GrowthInvesting",
    "DividendInvesting",
    "TechnicalTrading",
    "MacroTrading",
    "ActivistInvesting",
    "PassiveInvesting",
    "DefensiveValue",
    "GrowthAtReasonablePrice",
    "IncomeInvesting",
    "VictorAdlerInvesting",
    "LuizBarsiFilhoInvesting",
    "AllWeatherPortfolio",
    "OperationalExcellence",
    "AggressiveInvesting",
] 