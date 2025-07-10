from src.models.dto import DadosFinanceiros, AnaliseResultado

class ValueInvesting:
    nome = "warren_buffett"
    descricao = (
        "Foco em empresas sólidas, vantagem competitiva (moat), "
        "gestão de qualidade, geração de caixa e compra com margem de segurança."
    )
    indicadores = [
        "P/E ratio", "ROE", "Debt/Equity", "Free Cash Flow", "Moat"
    ]
    exemplos = [
        "Apple", "Coca-Cola", "Verisign", "GEICO", "BNSF Railway"
    ]
    referencias = [
        "The Intelligent Investor",
        "Essays of Warren Buffett",
        "https://www.investopedia.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Critérios de Buffett
        # 1. P/E razoável (< 15 é bom, < 25 aceitável)
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 20
                pontos_fortes.append(f"P/E excelente: {dados.pe_ratio:.2f}")
            elif dados.pe_ratio < 25:
                score += 10
                pontos_fortes.append(f"P/E razoável: {dados.pe_ratio:.2f}")
            else:
                pontos_fracos.append(f"P/E alto: {dados.pe_ratio:.2f}")

        # 2. ROE alto (> 15% é bom)
        if dados.roe:
            if dados.roe > 15:
                score += 20
                pontos_fortes.append(f"ROE excelente: {dados.roe:.2f}%")
            elif dados.roe > 10:
                score += 10
                pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
            else:
                pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # 3. Dívida controlada (D/E < 0.5 é bom)
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.3:
                score += 15
                pontos_fortes.append(f"Dívida muito baixa: {dados.debt_to_equity:.2f}")
            elif dados.debt_to_equity < 0.5:
                score += 10
                pontos_fortes.append(f"Dívida controlada: {dados.debt_to_equity:.2f}")
            else:
                pontos_fracos.append(f"Dívida alta: {dados.debt_to_equity:.2f}")

        # 4. Margem de lucro (> 10% é bom)
        if dados.profit_margin:
            if dados.profit_margin > 15:
                score += 15
                pontos_fortes.append(f"Margem de lucro excelente: {dados.profit_margin:.2f}%")
            elif dados.profit_margin > 10:
                score += 10
                pontos_fortes.append(f"Margem de lucro boa: {dados.profit_margin:.2f}%")
            else:
                pontos_fracos.append(f"Margem de lucro baixa: {dados.profit_margin:.2f}%")

        # 5. Crescimento consistente
        if dados.earnings_growth:
            if dados.earnings_growth > 10:
                score += 15
                pontos_fortes.append(f"Crescimento de lucros forte: {dados.earnings_growth:.2f}%")
            elif dados.earnings_growth > 5:
                score += 10
                pontos_fortes.append(f"Crescimento de lucros moderado: {dados.earnings_growth:.2f}%")
            else:
                pontos_fracos.append(f"Crescimento de lucros baixo: {dados.earnings_growth:.2f}%")

        # 6. Free Cash Flow positivo
        if dados.free_cash_flow and dados.free_cash_flow > 0:
            score += 15
            pontos_fortes.append("Free Cash Flow positivo")
        elif dados.free_cash_flow:
            pontos_fracos.append("Free Cash Flow negativo")

        # Determinar recomendação
        if score >= 70:
            recomendacao = "COMPRA"
        elif score >= 40:
            recomendacao = "NEUTRO"
        else:
            recomendacao = "VENDA"

        # Calcular preço alvo (método simplificado)
        preco_alvo = None
        if dados.earnings_per_share and dados.earnings_growth:
            pe_alvo = min(15, dados.earnings_growth)  # P/E conservador
            eps_futuro = dados.earnings_per_share * (1 + dados.earnings_growth / 100)
            preco_alvo = eps_futuro * pe_alvo

        return AnaliseResultado(
            symbol=dados.symbol,
            score=score,
            recomendacao=recomendacao,
            metodologia_aplicada="Warren Buffett - Value Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            preco_alvo=preco_alvo,
            justificativa="Análise baseada nos critérios de Buffett: empresas com vantagem competitiva, boa gestão e preço razoável."
        ) 