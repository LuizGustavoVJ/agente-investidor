from src.models.dto import DadosFinanceiros, AnaliseResultado
from src.models.finance_utils import calcular_margem_seguranca

class DefensiveValue:
    nome = "benjamin_graham"
    descricao = (
        "Foco em segurança do principal, análise fundamentalista, "
        "margem de segurança, empresas com dívida controlada."
    )
    indicadores = [
        "P/E ratio", "P/B ratio", "Debt/Equity", "Current Ratio",
        "Dividend Yield"
    ]
    exemplos = [
        "GEICO"
    ]
    referencias = [
        "Security Analysis",
        "The Intelligent Investor",
        "https://www.nordinvestimentos.com.br"
    ]

    @staticmethod
    def analisar(dados: DadosFinanceiros) -> AnaliseResultado:
        score = 0
        pontos_fortes = []
        pontos_fracos = []

        # Critérios de Graham
        # 1. P/E < 15
        if dados.pe_ratio:
            if dados.pe_ratio < 15:
                score += 25
                pontos_fortes.append(
                    f"P/E dentro do critério Graham: {dados.pe_ratio:.2f}"
                )
            else:
                pontos_fracos.append(
                    f"P/E acima do critério Graham: {dados.pe_ratio:.2f}"
                )

        # 2. P/B < 1.5
        if dados.pb_ratio:
            if dados.pb_ratio < 1.5:
                score += 20
                pontos_fortes.append(
                    f"P/B excelente: {dados.pb_ratio:.2f}"
                )
            elif dados.pb_ratio < 2.5:
                score += 10
                pontos_fortes.append(
                    f"P/B aceitável: {dados.pb_ratio:.2f}"
                )
            else:
                pontos_fracos.append(
                    f"P/B alto: {dados.pb_ratio:.2f}"
                )

        # 3. Current Ratio > 2
        if dados.current_ratio:
            if dados.current_ratio > 2:
                score += 20
                pontos_fortes.append(
                    f"Liquidez excelente: {dados.current_ratio:.2f}"
                )
            elif dados.current_ratio > 1.5:
                score += 10
                pontos_fortes.append(
                    f"Liquidez boa: {dados.current_ratio:.2f}"
                )
            else:
                pontos_fracos.append(
                    f"Liquidez baixa: {dados.current_ratio:.2f}"
                )

        # 4. Debt/Equity < 0.5
        if dados.debt_to_equity:
            if dados.debt_to_equity < 0.5:
                score += 20
                pontos_fortes.append(
                    f"Dívida controlada: {dados.debt_to_equity:.2f}"
                )
            else:
                pontos_fracos.append(
                    f"Dívida alta: {dados.debt_to_equity:.2f}"
                )

        # 5. Dividend Yield > 0 (empresas que pagam dividendos)
        if dados.dividend_yield and dados.dividend_yield > 0:
            score += 15
            pontos_fortes.append(
                f"Paga dividendos: {dados.dividend_yield:.2f}%"
            )

        # Calcular margem de segurança
        margem_seguranca = None
        if dados.book_value_per_share:
            valor_intrinseco = dados.book_value_per_share * 1.5  # Conservador
            margem_seguranca = calcular_margem_seguranca(
                dados.price, valor_intrinseco)
            if margem_seguranca > 30:
                score += 20
                pontos_fortes.append(
                    f"Excelente margem de segurança: {margem_seguranca:.1f}%"
                )
            elif margem_seguranca > 15:
                score += 10
                pontos_fortes.append(
                    f"Boa margem de segurança: {margem_seguranca:.1f}%"
                )
            else:
                pontos_fracos.append(
                    f"Margem de segurança insuficiente: {margem_seguranca:.1f}%"
                )

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
            metodologia_aplicada="Benjamin Graham - Defensive Value",
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            margem_seguranca=margem_seguranca,
            justificativa=(
                "Análise baseada nos critérios defensivos de Graham: "
                "segurança do principal e margem de segurança."
            )
        ) 