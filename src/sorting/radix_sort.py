def _counting_pass_desc(pairs, exp: int, base: int):
    """Una pasada estable de Counting Sort sobre el dígito (freq // exp) % base."""
    count = [0] * base
    for _, freq in pairs:
        count[(freq // exp) % base] += 1

    start = [0] * base
    total = 0
    for d in range(base - 1, -1, -1):
        start[d] = total
        total += count[d]

    output = [None] * len(pairs)
    for pair in pairs:
        d = (pair[1] // exp) % base
        output[start[d]] = pair
        start[d] += 1
    return output


def radix_sort_desc(
    pairs: list[tuple[str, int]], base: int = 10
) -> list[tuple[str, int]]:
    """LSD Radix Sort descendente por frecuencia. O(d * (n + base))."""
    if not pairs:
        return []

    max_val = max(freq for _, freq in pairs)
    output = list(pairs)
    exp = 1
    while max_val // exp > 0:
        output = _counting_pass_desc(output, exp, base)
        exp *= base
    return output