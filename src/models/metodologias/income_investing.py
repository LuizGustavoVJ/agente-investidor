class IncomeInvesting:
    nome = "Income Investing"
    descricao = (
        "Foco em geração de renda passiva, ações pagadoras de dividendos, "
        "compra para longo prazo."
    )
    indicadores = [
        "Dividend Yield", "Payout Ratio", "Dividend Growth", "ROE", "Debt/Equity"
    ]
    exemplos = [
        "Bancos brasileiros", "Utilities", "REITs"
    ]
    referencias = [
        "Ações que Pagam Dividendos",
        "https://www.fundamentus.com.br"
    ]

    @staticmethod
    def analisar(dados):
        return "Análise Income Investing não implementada." 