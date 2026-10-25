import random
from collections import Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from benchmark import ALGORITHMS, RESULTS, load_pairs, measure, python_sorted, write_csv

SIZES = [1_000, 10_000, 100_000, 1_000_000]


def corpus_distribution(pairs) -> None:
    n = len(pairs)
    counts = Counter(freq for _, freq in pairs)
    print("Distribución de frecuencias en el corpus:")
    cumulative = 0
    for f in sorted(counts)[:8]:
        cumulative += counts[f]
        print(
            f"  frecuencia {f:>2}: {counts[f]:>4} términos ({counts[f] / n:6.1%})"
            f" | acumulado {cumulative / n:6.1%}"
        )

    ranked = python_sorted(pairs)
    cut = ranked[14][1]
    tied = [t for t, f in ranked if f == cut]
    print(f"\nTérminos con frecuencia {cut} (la del puesto 15): {tied}")


def run_fixed_k(pairs) -> None:
    real = [f for _, f in pairs]
    k = max(real)
    algos = {**ALGORITHMS, "sorted() de Python": python_sorted}
    rows = []
    print(f"\nEscalamiento con k fijo = {k} (frecuencias remuestreadas del corpus):")
    for n in SIZES:
        rng = random.Random(42)
        data = [(f"t{i:07d}", f) for i, f in enumerate(rng.choices(real, k=n))]
        reference = python_sorted(data)
        repeats = 10 if n <= 10_000 else 5 if n <= 100_000 else 3
        for name, fn in algos.items():
            if fn(data) != reference:  # también sirve de calentamiento
                raise SystemExit(f"[ERROR] {name} falló con n = {n}")
            s = measure(fn, data, repeats, warmup=False)
            us = s["mean_ms"] * 1000 / n
            rows.append({"n": n, "algorithm": name, **s, "us_per_term": us})
            print(f"  n = {n:>9,} | {name:<22} {s['mean_ms']:>10.3f} ms | {us:6.3f} µs/término")

    write_csv(
        RESULTS / "timings_fixed_k.csv",
        ["n", "algorithm", "mean_ms", "median_ms", "min_ms", "stdev_ms", "us_per_term"],
        rows,
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    for name in algos:
        pts = [(r["n"], r["us_per_term"]) for r in rows if r["algorithm"] == name]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label=name)
    ax.set_xscale("log")
    ax.set_xlabel("Número de términos únicos (n)")
    ax.set_ylabel("Tiempo por término (µs)")
    ax.set_title(f"Tiempo por término con k fijo = {k} (plano = lineal)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "timings_fixed_k.png", dpi=150)
    plt.close(fig)


def main() -> None:
    pairs = load_pairs()
    corpus_distribution(pairs)
    run_fixed_k(pairs)


if __name__ == "__main__":
    main()