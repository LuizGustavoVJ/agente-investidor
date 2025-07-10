from src.models.dto import DadosFinanceiros, AnaliseResultado

class IncomeInvesting:
    nome = "dividendos"
    descricao = (
        "Foco em ações brasileiras pagadoras de dividendos, estabilidade de renda, "
        "payout sustentável e empresas sólidas do setor elétrico, bancos, etc."
    )
    indicadores = [
        "Dividend Yield", "Payout Ratio", "Dividend Growth", "ROE", "Debt/Equity"
    ]
    exemplos = [
        "TAEE11", "ITUB4", "BBAS3", "EGIE3", "B3SA3"
    ]
    referencias = [
        "Luiz Barsi Filho - Rei dos Dividendos",
        "https://www.fundamentus.com.br"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Dividend Yield Brasil: > 6% excelente, > 4% bom
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

        # Payout ratio sustentável (< 80%)
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

        # Estabilidade: dividendos pagos nos últimos 5 anos (simulação)
        dividendos_estaveis = getattr(dados, 'dividendos_estaveis', True)
        if dividendos_estaveis:
            score += 15
            pontos_fortes.append("Histórico de dividendos estável nos últimos anos")
        else:
            pontos_fracos.append("Dividendos instáveis ou irregulares")

        # ROE > 12%
        if dados.roe:
            if dados.roe > 15:
                score += 15
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 12:
                score += 10
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # Dívida controlada
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 10
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

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
            metodologia_aplicada="Luiz Barsi Filho - Dividendos Brasil",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em dividendos estáveis, payout sustentável e empresas sólidas brasileiras."
        ) 