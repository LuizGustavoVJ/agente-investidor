from src.models.dto import DadosFinanceiros, AnaliseResultado

class GrowthInvesting:
    nome = "seth_klarman"
    descricao = (
        "Estratégia deep value, busca por ativos descontados, margem de segurança elevada, "
        "abordagem contrária e assimétrica."
    )
    indicadores = [
        "Margem de Segurança", "P/L", "P/VP", "Crescimento de Lucros"
    ]
    exemplos = [
        "Ações fora do radar", "Empresas em recuperação"
    ]
    referencias = [
        "Margin of Safety",
        "https://baupost.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Margem de segurança (simulação)
        margem = getattr(dados, 'margem_seguranca', 25)
        if margem > 30:
            score += 30
            pontos_fortes.append(f"Margem de segurança muito alta: {margem:.1f}%")
        elif margem > 15:
            score += 20
            pontos_fortes.append(f"Boa margem de segurança: {margem:.1f}%")
        else:
            pontos_fracos.append(f"Margem de segurança baixa: {margem:.1f}%")

        # P/L baixo
        if dados.pe_ratio and dados.pe_ratio < 12:
            score += 20
            pontos_fortes.append(f"P/L baixo: {dados.pe_ratio:.2f}")
        elif dados.pe_ratio:
            pontos_fracos.append(f"P/L alto: {dados.pe_ratio:.2f}")

        # P/VP baixo
        if dados.pb_ratio and dados.pb_ratio < 1.2:
            score += 15
            pontos_fortes.append(f"P/VP baixo: {dados.pb_ratio:.2f}")
        elif dados.pb_ratio:
            pontos_fracos.append(f"P/VP alto: {dados.pb_ratio:.2f}")

        # Crescimento de lucros (simulação)
        crescimento = getattr(dados, 'earnings_growth', 0.08)
        if crescimento > 0.1:
            score += 15
            pontos_fortes.append(f"Crescimento de lucros consistente: {crescimento*100:.1f}% ao ano")
        else:
            pontos_fracos.append(f"Crescimento de lucros baixo: {crescimento*100:.1f}% ao ano")

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
            metodologia_aplicada="Seth Klarman - Deep Value/Contrária",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em margem de segurança, valor descontado e abordagem contrária."
        )

class AggressiveInvesting:
    nome = "lirio_parisotto"
    descricao = (
        "Investimento agressivo, busca por grandes ganhos, alta exposição, "
        "aceitação de volatilidade e possíveis perdas."
    )
    indicadores = [
        "Volatilidade", "Alavancagem", "Potencial de Retorno", "Exposição Setorial"
    ]
    exemplos = [
        "Ações small caps", "Setores cíclicos"
    ]
    referencias = [
        "Lírio Parisotto - Investidor Agressivo",
        "https://www.valor.com.br"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Volatilidade alta
        volatilidade = getattr(dados, 'volatilidade', 0.04)
        if volatilidade > 0.03:
            score += 30
            pontos_fortes.append(f"Volatilidade alta: {volatilidade*100:.2f}%")
        else:
            pontos_fracos.append(f"Volatilidade baixa: {volatilidade*100:.2f}%")

        # Alavancagem
        alavancagem = getattr(dados, 'alavancagem', 1.2)
        if alavancagem > 1.1:
            score += 25
            pontos_fortes.append(f"Alavancagem elevada: {alavancagem:.2f}x")
        else:
            pontos_fracos.append(f"Alavancagem baixa: {alavancagem:.2f}x")

        # Potencial de retorno (simulação)
        potencial = getattr(dados, 'potencial_retorno', 0.18)
        if potencial > 0.15:
            score += 25
            pontos_fortes.append(f"Potencial de retorno elevado: {potencial*100:.1f}% ao ano")
        else:
            pontos_fracos.append(f"Potencial de retorno baixo: {potencial*100:.1f}% ao ano")

        # Exposição setorial (simulação)
        exposicao = getattr(dados, 'exposicao_setorial', 0.5)
        if exposicao > 0.4:
            score += 10
            pontos_fortes.append(f"Exposição setorial relevante: {exposicao*100:.1f}%")
        else:
            pontos_fracos.append(f"Exposição setorial baixa: {exposicao*100:.1f}%")

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
            metodologia_aplicada="Lírio Parisotto - Investidor Agressivo",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em volatilidade, alavancagem e potencial de retorno agressivo."
        ) 