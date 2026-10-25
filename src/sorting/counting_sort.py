def counting_sort_desc(pairs: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """Ordena (término, frecuencia) por frecuencia descendente. Estable. O(n + k)."""
    if not pairs:
        return []

    k = max(freq for _, freq in pairs)

    # 1. Contar cuántos términos hay con cada frecuencia
    count = [0] * (k + 1)
    for _, freq in pairs:
        count[freq] += 1

    # 2. start[v] = cuántos elementos tienen frecuencia mayor que v
    start = [0] * (k + 1)
    total = 0
    for v in range(k, -1, -1):
        start[v] = total
        total += count[v]

    # 3. Colocar cada elemento en su posición final (recorriendo en orden de entrada)
    output = [None] * len(pairs)
    for pair in pairs:
        freq = pair[1]
        output[start[freq]] = pair
        start[freq] += 1
    return output