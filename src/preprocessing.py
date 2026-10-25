import json
import re
from collections import Counter
from pathlib import Path

import nltk
from nltk.corpus import stopwords

ABSTRACTS = Path("data/processed/abstracts.json")


def load_stopwords() -> set[str]:
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords")
        return set(stopwords.words("english"))


def tokenize(text: str) -> list[str]:
    # Minúsculas, solo letras, mínimo 2 caracteres ("AI" se conserva)
    return re.findall(r"[a-z]{2,}", text.lower())


def preprocess(text: str, stop: set[str]) -> list[str]:
    return [t for t in tokenize(text) if t not in stop]


def glued_candidates(all_tokens: list[str], stop: set[str]) -> list[tuple]:
    """Posibles palabras pegadas: stopword + palabra, o palabra + stopword."""
    vocab = set(all_tokens)
    found = []
    for t in vocab:
        if len(t) < 8:
            continue
        for i in range(1, 5):
            head, tail = t[:i], t[i:]
            if head in stop and tail in vocab and len(tail) >= 4:
                found.append((t, head, tail))
            head, tail = t[:-i], t[-i:]
            if tail in stop and head in vocab and len(head) >= 4:
                found.append((t, head, tail))
    return sorted(set(found))


def main() -> None:
    data = json.loads(ABSTRACTS.read_text(encoding="utf-8"))
    stop = load_stopwords()

    all_tokens, terms = [], []
    for item in data:
        all_tokens += tokenize(item["abstract"])
        terms += preprocess(item["abstract"], stop)

    freq = Counter(terms)
    print(f"Tokens (sin stopwords): {len(terms)} | términos únicos: {len(freq)}\n")

    print("Top 30 términos:")
    for term, count in freq.most_common(30):
        print(f"  {term:<20} {count}")

    print("\nPosibles palabras pegadas (revisar a mano):")
    for token, a, b in glued_candidates(all_tokens, stop):
        print(f"  {token:<25} -> {a} + {b}")


if __name__ == "__main__":
    main()