from src.models.dto import DadosFinanceiros, AnaliseResultado

class TechnicalTrading:
    nome = "linda_bradford_raschke"
    descricao = (
        "Estratégia de trading técnico, day-trading e swing trading, foco em volatilidade, liquidez e padrões gráficos. "
        "Exige disciplina, controle de risco e execução rápida."
    )
    indicadores = [
        "Volatilidade", "Liquidez", "Tendência", "Volume"
    ]
    exemplos = [
        "Ações de alta liquidez", "Índices futuros", "Forex"
    ]
    referencias = [
        "Trading Sardines",
        "https://lindaraschke.net"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Volatilidade alta é positiva para trading
        volatilidade = getattr(dados, 'volatilidade', 0.03)
        if volatilidade > 0.025:
            score += 30
            pontos_fortes.append(f"Volatilidade alta: {volatilidade*100:.2f}%")
        else:
            pontos_fracos.append(f"Volatilidade baixa: {volatilidade*100:.2f}%")

        # Liquidez (simulação)
        liquidez = getattr(dados, 'liquidez', 1e7)
        if liquidez > 1e6:
            score += 25
            pontos_fortes.append(f"Alta liquidez: R$ {liquidez:,.0f}")
        else:
            pontos_fracos.append(f"Liquidez baixa: R$ {liquidez:,.0f}")

        # Tendência (simulação)
        tendencia = getattr(dados, 'tendencia', 1)
        if tendencia > 0:
            score += 20
            pontos_fortes.append("Tendência de alta identificada")
        else:
            pontos_fracos.append("Sem tendência clara")

        # Frequência de operações (simulação)
        freq = getattr(dados, 'frequencia_operacoes', 5)
        if freq > 3:
            score += 15
            pontos_fortes.append(f"Alta frequência de operações: {freq} trades/dia")
        else:
            pontos_fracos.append(f"Frequência de operações baixa: {freq} trades/dia")

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
            metodologia_aplicada="Linda Bradford Raschke - Technical Trading",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            justificativa="Análise baseada em volatilidade, liquidez e padrões técnicos para trading ativo."
        ) 