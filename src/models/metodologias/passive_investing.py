from src.models.dto import DadosFinanceiros, AnaliseResultado

class PassiveInvesting:
    nome = "john_bogle"
    descricao = (
        "Fundo indexado, investimento passivo, minimização de taxas, "
        "foco em retorno de mercado a longo prazo."
    )
    indicadores = [
        "Expense Ratio", "Tracking Error", "Market Beta"
    ]
    exemplos = [
        "S&P 500 Index", "Total Stock Market Index"
    ]
    referencias = [
        "Common Sense on Mutual Funds",
        "The Little Book of Common Sense Investing",
        "https://www.vanguard.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Simulação: se o símbolo for de ETF conhecido, dar pontos
        etfs_indexados = ["IVV", "VOO", "SPY", "BOVA11", "VTI", "QQQ"]
        if dados.symbol.upper() in etfs_indexados:
            score += 40
            pontos_fortes.append(f"{dados.symbol} é um ETF indexado reconhecido.")
        else:
            pontos_fracos.append(f"{dados.symbol} não é um ETF indexado clássico.")

        # Taxa de administração (expense ratio) - quanto menor, melhor
        # Simulação: se não houver, assume 0.15% (baixo)
        expense_ratio = getattr(dados, 'expense_ratio', 0.15)
        if expense_ratio < 0.2:
            score += 25
            pontos_fortes.append(f"Taxa de administração muito baixa: {expense_ratio*100:.2f}%")
        elif expense_ratio < 0.5:
            score += 15
            pontos_fortes.append(f"Taxa de administração razoável: {expense_ratio*100:.2f}%")
        else:
            pontos_fracos.append(f"Taxa de administração alta: {expense_ratio*100:.2f}%")

        # Tracking error (quanto menor, melhor)
        tracking_error = getattr(dados, 'tracking_error', 0.01)
        if tracking_error < 0.02:
            score += 15
            pontos_fortes.append(f"Tracking error muito baixo: {tracking_error*100:.2f}%")
        elif tracking_error < 0.05:
            score += 8
            pontos_fortes.append(f"Tracking error razoável: {tracking_error*100:.2f}%")
        else:
            pontos_fracos.append(f"Tracking error elevado: {tracking_error*100:.2f}%")

        # Diversificação (simulação: market_cap alto)
        if dados.market_cap and dados.market_cap > 1e10:
            score += 10
            pontos_fortes.append("Alta diversificação (grande capitalização de mercado)")
        else:
            pontos_fracos.append("Baixa diversificação (market cap baixo)")

        # Volatilidade (simulação: beta próximo de 1)
        beta = getattr(dados, 'beta', 1.0)
        if 0.9 <= beta <= 1.1:
            score += 10
            pontos_fortes.append(f"Volatilidade de mercado adequada (Beta={beta:.2f})")
        else:
            pontos_fracos.append(f"Volatilidade fora do padrão de índice (Beta={beta:.2f})")

        # Recomendação
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
            metodologia_aplicada="John Bogle - Passive/Index Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em investimento passivo: baixo custo, diversificação e aderência ao índice."
        ) 