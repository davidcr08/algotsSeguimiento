def _insertion_sort_desc(items: list) -> None:
    """Insertion sort estable (frecuencia descendente), en el lugar."""
    for i in range(1, len(items)):
        current = items[i]
        j = i - 1
        while j >= 0 and items[j][1] < current[1]:  # '<' estricto => estable
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = current


def bucket_sort_desc(
    pairs: list[tuple[str, int]], num_buckets: int | None = None
) -> list[tuple[str, int]]:
    """Bucket Sort descendente por frecuencia.

    Por defecto usa n buckets (versión clásica). El parámetro num_buckets
    permite experimentar con menos buckets para el análisis.
    """
    n = len(pairs)
    if n == 0:
        return []

    m = num_buckets or n
    max_val = max(freq for _, freq in pairs)

    # Bucket i recibe las frecuencias del rango i (el índice crece con la frecuencia)
    buckets: list[list] = [[] for _ in range(m)]
    for pair in pairs:
        buckets[pair[1] * m // (max_val + 1)].append(pair)

    output: list = []
    for bucket in reversed(buckets):  # del bucket de mayor frecuencia al menor
        _insertion_sort_desc(bucket)
        output.extend(bucket)
    return output