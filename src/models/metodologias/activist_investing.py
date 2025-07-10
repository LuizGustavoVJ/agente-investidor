from src.models.dto import DadosFinanceiros, AnaliseResultado

class ActivistInvesting:
    nome = "carl_icahn"
    descricao = (
        "Investimento ativista, busca por mudanças em empresas, foco em governança, eficiência e destravamento de valor. "
        "Alta exposição e potencial de retorno, mas exige conhecimento e influência."
    )
    indicadores = [
        "Governança", "Potencial de Reestruturação", "Participação Acionária", "ROE"
    ]
    exemplos = [
        "Icahn Enterprises", "Empresas em turnaround"
    ]
    referencias = [
        "Carl Icahn - Activist Investing",
        "https://www.icahnenterprises.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Governança (simulação)
        governanca = getattr(dados, 'governanca', 0.8)
        if governanca > 0.7:
            score += 30
            pontos_fortes.append("Boa governança corporativa")
        else:
            pontos_fracos.append("Governança corporativa fraca")

        # Potencial de reestruturação (simulação)
        turnaround = getattr(dados, 'turnaround', 0.6)
        if turnaround > 0.5:
            score += 25
            pontos_fortes.append("Potencial de reestruturação identificado")
        else:
            pontos_fracos.append("Pouco potencial de turnaround")

        # Participação acionária relevante (simulação)
        participacao = getattr(dados, 'participacao_acionaria', 0.12)
        if participacao > 0.1:
            score += 20
            pontos_fortes.append(f"Participação acionária relevante: {participacao*100:.1f}%")
        else:
            pontos_fracos.append(f"Participação acionária baixa: {participacao*100:.1f}%")

        # ROE
        if dados.roe and dados.roe > 10:
            score += 15
            pontos_fortes.append(f"ROE bom: {dados.roe:.2f}%")
        elif dados.roe:
            pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

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
            metodologia_aplicada="Carl Icahn - Activist Investing",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em governança, potencial de turnaround e ativismo acionário."
        )

class OperationalExcellence:
    nome = "jorge_paulo_lemann"
    descricao = (
        "Foco em eficiência operacional, geração de valor, liderança de mercado e cultura de resultados. "
        "Busca empresas com histórico de crescimento e margens elevadas."
    )
    indicadores = [
        "Margem Operacional", "Crescimento de Receita", "ROE", "Liderança de Mercado"
    ]
    exemplos = [
        "Ambev", "3G Capital", "Burger King"
    ]
    referencias = [
        "Jorge Paulo Lemann - Eficiência Operacional",
        "https://www.3g-capital.com"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Margem operacional (simulação)
        margem_op = getattr(dados, 'operating_margin', 0.18)
        if margem_op > 0.15:
            score += 30
            pontos_fortes.append(f"Margem operacional elevada: {margem_op*100:.1f}%")
        else:
            pontos_fracos.append(f"Margem operacional baixa: {margem_op*100:.1f}%")

        # Crescimento de receita (simulação)
        crescimento = getattr(dados, 'revenue_growth', 0.12)
        if crescimento > 0.1:
            score += 25
            pontos_fortes.append(f"Crescimento de receita consistente: {crescimento*100:.1f}% ao ano")
        else:
            pontos_fracos.append(f"Crescimento de receita baixo: {crescimento*100:.1f}% ao ano")

        # ROE
        if dados.roe and dados.roe > 12:
            score += 20
            pontos_fortes.append(f"ROE elevado: {dados.roe:.2f}%")
        elif dados.roe:
            pontos_fracos.append(f"ROE baixo: {dados.roe:.2f}%")

        # Liderança de mercado (simulação)
        lider = getattr(dados, 'lideranca_mercado', True)
        if lider:
            score += 15
            pontos_fortes.append("Empresa líder de mercado")
        else:
            pontos_fracos.append("Empresa sem liderança de mercado")

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
            metodologia_aplicada="Jorge Paulo Lemann - Eficiência Operacional",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em eficiência operacional, crescimento e liderança de mercado."
        ) 