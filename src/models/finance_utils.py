def calcular_margem_seguranca(
    preco_atual: float, valor_intrinseco: float
) -> float:
    """
    Calcula a margem de segurança percentual entre preço atual
    e valor intrínseco.
    """
    if valor_intrinseco <= 0:
        return 0
    return ((valor_intrinseco - preco_atual) / valor_intrinseco) * 100 