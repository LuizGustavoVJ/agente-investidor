from src.models.dto import DadosFinanceiros, AnaliseResultado

class MacroTrading:
    nome = "george_soros"
    descricao = (
        "Estratégia macro global, foco em grandes tendências econômicas, moedas, juros e commodities. "
        "Alta volatilidade, exige conhecimento de cenários globais."
    )
    indicadores = [
        "Volatilidade", "Alavancagem", "Exposição Cambial", "Tendência de Mercado"
    ]
    exemplos = [
        "Soros Fund Management", "Quantum Fund"
    ]
    referencias = [
        "The Alchemy of Finance",
        "https://www.soros.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Simulação: volatilidade alta pode ser positiva para macro trading
        volatilidade = getattr(dados, 'volatilidade', 0.25)
        if volatilidade > 0.2:
            score += 30
            pontos_fortes.append(f"Alta volatilidade: {volatilidade*100:.1f}% (potencial para grandes movimentos)")
        else:
            pontos_fracos.append(f"Volatilidade baixa: {volatilidade*100:.1f}% (pouco potencial para macro trades)")

        # Exposição cambial (simulação)
        exposicao_cambial = getattr(dados, 'exposicao_cambial', 0.5)
        if exposicao_cambial > 0.3:
            score += 20
            pontos_fortes.append(f"Exposição cambial relevante: {exposicao_cambial*100:.1f}%")
        else:
            pontos_fracos.append(f"Baixa exposição cambial: {exposicao_cambial*100:.1f}%")

        # Alavancagem (simulação)
        alavancagem = getattr(dados, 'alavancagem', 1.0)
        if alavancagem > 1.5:
            score += 20
            pontos_fortes.append(f"Alavancagem alta: {alavancagem:.2f}x")
        else:
            pontos_fracos.append(f"Alavancagem baixa: {alavancagem:.2f}x")

        # Tendência de mercado (simulação)
        tendencia = getattr(dados, 'tendencia_mercado', 1)
        if tendencia > 0:
            score += 20
            pontos_fortes.append("Tendência de alta identificada")
        else:
            pontos_fracos.append("Mercado sem tendência clara")

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
            metodologia_aplicada="George Soros - Macro Trading",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em macro trading: volatilidade, exposição cambial e tendências globais."
        )

class AllWeatherPortfolio:
    nome = "ray_dalio"
    descricao = (
        "Carteira balanceada para todos os cenários econômicos, diversificação entre ações, renda fixa, ouro e commodities. "
        "Foco em robustez e resiliência."
    )
    indicadores = [
        "Diversificação", "Risco", "Alocação em Ativos", "Volatilidade"
    ]
    exemplos = [
        "Carteira All Weather", "Bridgewater Associates"
    ]
    referencias = [
        "Principles for Navigating Big Debt Crises",
        "https://www.bridgewater.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Diversificação (simulação: market_cap alto e vários setores)
        diversificacao = getattr(dados, 'diversificacao', 0.8)
        if diversificacao > 0.7:
            score += 30
            pontos_fortes.append("Alta diversificação entre ativos e setores")
        else:
            pontos_fracos.append("Diversificação insuficiente")

        # Risco (simulação: volatilidade baixa/moderada)
        volatilidade = getattr(dados, 'volatilidade', 0.15)
        if volatilidade < 0.2:
            score += 25
            pontos_fortes.append(f"Volatilidade controlada: {volatilidade*100:.1f}%")
        else:
            pontos_fracos.append(f"Volatilidade elevada: {volatilidade*100:.1f}%")

        # Alocação em renda fixa (simulação)
        renda_fixa = getattr(dados, 'renda_fixa', 0.3)
        if renda_fixa > 0.25:
            score += 20
            pontos_fortes.append(f"Boa alocação em renda fixa: {renda_fixa*100:.1f}%")
        else:
            pontos_fracos.append(f"Pouca alocação em renda fixa: {renda_fixa*100:.1f}%")

        # Ouro/commodities (simulação)
        ouro = getattr(dados, 'ouro', 0.07)
        if ouro > 0.05:
            score += 15
            pontos_fortes.append(f"Exposição a ouro/commodities: {ouro*100:.1f}%")
        else:
            pontos_fracos.append(f"Baixa exposição a ouro/commodities: {ouro*100:.1f}%")

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
            metodologia_aplicada="Ray Dalio - All Weather Portfolio",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em diversificação, controle de risco e robustez da carteira."
        ) 