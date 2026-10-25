import csv
import json
import random
import statistics
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo guarda PNG
import matplotlib.pyplot as plt

from sorting.bucket_sort import bucket_sort_desc
from sorting.counting_sort import counting_sort_desc
from sorting.radix_sort import radix_sort_desc

FREQ_FILE = Path("data/processed/frequencies.json")
RESULTS = Path("results")

CORPUS_REPEATS = 300
SCALING_SIZES = [1_000, 4_000, 10_000, 100_000, 1_000_000]
BUCKET5_MAX_N = 4_000  # con pocos buckets el insertion sort interno se vuelve cuadrático


def bucket_sort_5(pairs):
    return bucket_sort_desc(pairs, num_buckets=5)


def python_sorted(pairs):
    # Referencia: estable, así que los empates conservan el orden alfabético de entrada
    return sorted(pairs, key=lambda p: -p[1])


ALGORITHMS = {
    "Counting Sort": counting_sort_desc,
    "Radix Sort": radix_sort_desc,
    "Bucket Sort": bucket_sort_desc,
}
EXTRAS = {
    "Bucket Sort (5 buckets)": bucket_sort_5,
    "sorted() de Python": python_sorted,
}


def load_pairs() -> list[tuple[str, int]]:
    raw = json.loads(FREQ_FILE.read_text(encoding="utf-8"))
    return [(term, freq) for term, freq in raw]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def measure(fn, data, repeats: int, warmup: bool = True) -> dict:
    """Tiempo de fn(data) en ms. Los algoritmos no modifican la entrada."""
    if warmup:
        fn(data)
    times = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        fn(data)
        times.append((time.perf_counter_ns() - start) / 1e6)
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
    }


# ---------- Validación y top 15 ----------

def validate(pairs):
    reference = python_sorted(pairs)
    outputs = {}
    for name, fn in {**ALGORITHMS, **EXTRAS}.items():
        out = fn(pairs)
        if out != reference:
            raise SystemExit(f"[ERROR] {name} no coincide con la referencia")
        outputs[name] = out
    return outputs


def save_top15(outputs) -> None:
    names = list(ALGORITHMS)
    rows = []
    for i in range(15):
        row = {"rank": i + 1}
        for name in names:
            term, freq = outputs[name][i]
            row[name] = f"{term} ({freq})"
        rows.append(row)
    write_csv(RESULTS / "top15.csv", ["rank", *names], rows)

    print(f"{'#':<4}" + "".join(f"{n:<24}" for n in names))
    for row in rows:
        print(f"{row['rank']:<4}" + "".join(f"{row[n]:<24}" for n in names))

    top = outputs["Counting Sort"][:15]
    terms = [t for t, _ in top][::-1]
    freqs = [f for _, f in top][::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(terms, freqs)
    ax.set_xlabel("Frecuencia")
    ax.set_title("Top 15 términos del corpus (idéntico en los 3 algoritmos)")
    fig.tight_layout()
    fig.savefig(RESULTS / "top15.png", dpi=150)
    plt.close(fig)


# ---------- Medición sobre el corpus ----------

def run_corpus(pairs):
    stats = {}
    for name, fn in {**ALGORITHMS, **EXTRAS}.items():
        stats[name] = measure(fn, pairs, CORPUS_REPEATS)

    print(f"\nTiempos sobre el corpus ({CORPUS_REPEATS} repeticiones, en ms):")
    print(f"{'Algoritmo':<26}{'media':>10}{'mediana':>10}{'mín':>10}{'desv.':>10}")
    for name, s in stats.items():
        print(
            f"{name:<26}{s['mean_ms']:>10.4f}{s['median_ms']:>10.4f}"
            f"{s['min_ms']:>10.4f}{s['stdev_ms']:>10.4f}"
        )

    rows = [
        {"algorithm": name, "n": len(pairs), "repeats": CORPUS_REPEATS, **s}
        for name, s in stats.items()
    ]
    write_csv(
        RESULTS / "timings_corpus.csv",
        ["algorithm", "n", "repeats", "mean_ms", "median_ms", "min_ms", "stdev_ms"],
        rows,
    )

    names = list(stats)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(
        range(len(names)),
        [stats[n]["mean_ms"] for n in names],
        yerr=[stats[n]["stdev_ms"] for n in names],
        capsize=4,
    )
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_ylabel("Tiempo (ms)")
    ax.set_title(f"Ordenamiento del corpus (n = {len(pairs)}, {CORPUS_REPEATS} repeticiones)")
    fig.tight_layout()
    fig.savefig(RESULTS / "timings_corpus.png", dpi=150)
    plt.close(fig)


# ---------- Escalamiento con datos sintéticos ----------

def synthetic_pairs(n: int, seed: int = 42) -> list[tuple[str, int]]:
    """Frecuencias tipo Zipf (f = n / rango), con k = n, asignadas al azar a términos
    que ya vienen en orden alfabético."""
    rng = random.Random(seed)
    freqs = [max(1, n // (r + 1)) for r in range(n)]
    rng.shuffle(freqs)
    return [(f"t{i:07d}", f) for i, f in enumerate(freqs)]


def run_scaling() -> None:
    rows = []
    print("\nEscalamiento con datos sintéticos (puede tardar uno o dos minutos):")
    for n in SCALING_SIZES:
        pairs = synthetic_pairs(n)
        repeats = 10 if n <= 10_000 else 5 if n <= 100_000 else 3
        algos = {**ALGORITHMS, "sorted() de Python": python_sorted}
        if n <= BUCKET5_MAX_N:
            algos["Bucket Sort (5 buckets)"] = bucket_sort_5

        reference = python_sorted(pairs)
        for name, fn in algos.items():
            if fn(pairs) != reference:  # esta llamada también hace de calentamiento
                raise SystemExit(f"[ERROR] {name} falló con n = {n}")
            s = measure(fn, pairs, repeats, warmup=False)
            rows.append({"n": n, "algorithm": name, **s})
            print(f"  n = {n:>9,} | {name:<26} {s['mean_ms']:>12.3f} ms")

    write_csv(
        RESULTS / "timings_scaling.csv",
        ["n", "algorithm", "mean_ms", "median_ms", "min_ms", "stdev_ms"],
        rows,
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    for name in dict.fromkeys(r["algorithm"] for r in rows):
        pts = [(r["n"], r["mean_ms"]) for r in rows if r["algorithm"] == name]
        ax.loglog([p[0] for p in pts], [p[1] for p in pts], marker="o", label=name)
    ax.set_xlabel("Número de términos únicos (n)")
    ax.set_ylabel("Tiempo medio (ms)")
    ax.set_title("Escalamiento con frecuencias tipo Zipf (k = n)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "timings_scaling.png", dpi=150)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    pairs = load_pairs()
    k = max(freq for _, freq in pairs)
    print(f"Corpus: n = {len(pairs)} términos únicos, k = {k}\n")

    outputs = validate(pairs)
    print("Validación OK: todos los algoritmos coinciden con la referencia.\n")
    save_top15(outputs)
    run_corpus(pairs)
    run_scaling()
    print(f"\nResultados guardados en {RESULTS}\\")


if __name__ == "__main__":
    main()