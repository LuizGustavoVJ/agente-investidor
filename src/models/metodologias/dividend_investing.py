from src.models.dto import DadosFinanceiros, AnaliseResultado

class DividendInvesting:
    nome = "Dividend Investing"
    descricao = (
        "Foco em geração de renda passiva, ações pagadoras de dividendos, "
        "compra para longo prazo, dividend yield alto e consistente."
    )
    indicadores = [
        "Dividend Yield", "Payout Ratio", "Dividend Growth", "ROE", "Debt/Equity",
        "Dividend History", "Price recovery potential", "Long-term value"
    ]
    exemplos = [
        "Bancos brasileiros", "Utilities", "REITs", "Blue-chip dividend stocks",
        "Eternit", "Oi", "Eletrobras"
    ]
    referencias = [
        "Ações que Pagam Dividendos",
        "Dividends Don't Lie",
        "https://www.fundamentus.com.br"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Critérios para investimento em dividendos
        # 1. Dividend Yield > 4%
        if dados.dividend_yield:
            if dados.dividend_yield > 6:
                score += 30
                pontos_fortes.append(f"Dividend yield excelente: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 4:
                score += 20
                pontos_fortes.append(f"Dividend yield bom: {dados.dividend_yield:.2f}%")
            elif dados.dividend_yield > 2:
                score += 10
                pontos_fortes.append(f"Dividend yield moderado: {dados.dividend_yield:.2f}%")
            else:
                pontos_fracos.append(f"Dividend yield baixo: {dados.dividend_yield:.2f}%")
        else:
            pontos_fracos.append("Não paga dividendos")

        # 2. Payout ratio sustentável (< 80%)
        if dados.earnings_per_share and dados.dividend_yield:
            dividend_per_share = dados.price * (dados.dividend_yield / 100)
            payout_ratio = (dividend_per_share / dados.earnings_per_share) * 100

            if payout_ratio < 60:
                score += 20
                pontos_fortes.append(f"Payout ratio sustentável: {payout_ratio:.1f}%")
            elif payout_ratio < 80:
                score += 10
                pontos_fortes.append(f"Payout ratio aceitável: {payout_ratio:.1f}%")
            else:
                pontos_fracos.append(f"Payout ratio alto: {payout_ratio:.1f}%")

        # 3. ROE > 12% (capacidade de gerar lucro)
        if dados.roe:
            if dados.roe > 15:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 12:
                score += 15
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # 4. Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 15
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

        # 5. Estabilidade (P/E não muito alto)
        if dados.pe_ratio:
            if dados.pe_ratio < 20:
                score += 15
                pontos_fortes.append(f"P/E estável: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")

        # Determinar recomendação
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
            metodologia_aplicada="Foco em Dividendos - Barsi/Weiss",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise focada em renda passiva: dividend yield alto, payout sustentável e empresa sólida."
        ) 