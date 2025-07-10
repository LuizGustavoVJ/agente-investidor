from src.models.dto import DadosFinanceiros, AnaliseResultado

class GrowthAtReasonablePrice:
    nome = "Growth at Reasonable Price"
    descricao = (
        "Crescimento dentro de valor, análise de PEG, foco em small caps promissoras "
        "e produtos familiares ao investidor."
    )
    indicadores = [
        "PEG ratio", "Earnings growth", "Revenue growth", "Market share"
    ]
    exemplos = [
        "Dunkin' Donuts", "Taco Bell", "Chrysler"
    ]
    referencias = [
        "One Up On Wall Street",
        "Beating the Street",
        "https://www.morningstar.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Critérios de Lynch
        # 1. PEG Ratio < 1 (ideal)
        if dados.peg_ratio:
            if dados.peg_ratio < 0.5:
                score += 30
                pontos_fortes.append(f"PEG excelente: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1:
                score += 20
                pontos_fortes.append(f"PEG bom: {dados.peg_ratio:.2f}")
            elif dados.peg_ratio < 1.5:
                score += 10
                pontos_fortes.append(f"PEG aceitável: {dados.peg_ratio:.2f}")
            else:
                pontos_fracos.append(f"PEG alto: {dados.peg_ratio:.2f}")

        # 2. Crescimento de receita > 10%
        if dados.revenue_growth:
            if dados.revenue_growth > 20:
                score += 25
                pontos_fortes.append(f"Crescimento de receita excelente: {dados.revenue_growth:.2f}%")
            elif dados.revenue_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento de receita bom: {dados.revenue_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento de receita baixo: {dados.revenue_growth:.2f}%")

        # 3. Crescimento de lucros > 15%
        if dados.earnings_growth:
            if dados.earnings_growth > 25:
                score += 25
                pontos_fortes.append(f"Crescimento de lucros excelente: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 15:
                score += 15
                pontos_fortes.append(f"Crescimento de lucros bom: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento de lucros baixo: {dados.earnings_growth:.2f}%")

        # 4. P/E razoável para o crescimento
        if dados.pe_ratio and dados.earnings_growth:
            pe_growth_ratio = dados.pe_ratio / dados.earnings_growth
            if pe_growth_ratio < 0.5:
                score += 20
                pontos_fortes.append(f"P/E baixo para o crescimento: {pe_growth_ratio:.2f}")
            elif pe_growth_ratio < 1:
                score += 10
                pontos_fortes.append(f"P/E razoável para o crescimento: {pe_growth_ratio:.2f}")

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
            metodologia_aplicada="Peter Lynch - Growth at Reasonable Price",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada nos critérios de Lynch: crescimento sustentável a preço razoável (PEG < 1)."
        ) 