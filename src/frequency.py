import json
from collections import Counter
from pathlib import Path

from preprocessing import load_terms

OUT_FILE = Path("data/processed/frequencies.json")


def build_frequencies() -> list[tuple[str, int]]:
    freq = Counter(load_terms())
    return sorted(freq.items())  # alfabético: NO viene ordenado por frecuencia


def main() -> None:
    pairs = build_frequencies()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(pairs, ensure_ascii=False), encoding="utf-8")

    max_freq = max(count for _, count in pairs)
    print(f"{len(pairs)} términos únicos | frecuencia máxima (k) = {max_freq}")
    print(f"Guardado en {OUT_FILE}")


if __name__ == "__main__":
    main()