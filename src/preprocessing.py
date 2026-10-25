import json
import re
import textwrap
from collections import Counter
from pathlib import Path

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

ABSTRACTS = Path("data/processed/abstracts.json")

# Interruptores para comparar el efecto de cada decisión en el ranking
USE_LEMMA = True
USE_DOMAIN_STOPWORDS = True

# Palabras funcionales del inglés que la lista de NLTK no incluye
EXTRA_STOPWORDS = {
    "although", "among", "could", "since", "towards",
    "upon", "whilst", "whereof", "would",
}

# Palabras genéricas de abstracts académicos (decisión de diseño: documentar en el informe)
DOMAIN_STOPWORDS = {
    "also", "based", "study", "studies", "paper", "papers",
    "article", "articles", "result", "results", "finding", "findings",
}

# Compuestas que quedaron pegadas al unir el guion de fin de línea
CORRECTIONS = {
    "instancebased": ["instance", "based"],
}


def ensure_nltk() -> None:
    for resource, path in [
        ("stopwords", "corpora/stopwords"),
        ("wordnet", "corpora/wordnet"),
    ]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource)


def tokenize(text: str) -> list[str]:
    # Minúsculas, solo letras, mínimo 2 caracteres ("ai" se conserva)
    return re.findall(r"[a-z]{2,}", text.lower())


def preprocess(text: str, stop: set[str], lemmatizer: WordNetLemmatizer) -> list[str]:
    tokens: list[str] = []
    for t in tokenize(text):
        tokens.extend(CORRECTIONS.get(t, [t]))
    tokens = [t for t in tokens if t not in stop]
    if USE_LEMMA:
        tokens = [lemmatizer.lemmatize(t, pos="n") for t in tokens]
    if USE_DOMAIN_STOPWORDS:
        tokens = [t for t in tokens if t not in DOMAIN_STOPWORDS]
    return tokens


def load_terms() -> list[str]:
    ensure_nltk()
    stop = set(stopwords.words("english")) | EXTRA_STOPWORDS
    lemmatizer = WordNetLemmatizer()
    data = json.loads(ABSTRACTS.read_text(encoding="utf-8"))
    terms: list[str] = []
    for item in data:
        terms += preprocess(item["abstract"], stop, lemmatizer)
    return terms


def main() -> None:
    terms = load_terms()
    freq = Counter(terms)
    print(f"Términos totales: {len(terms)} | únicos: {len(freq)}\n")

    print("Top 30:")
    for term, count in freq.most_common(30):
        print(f"  {term:<20} {count}")

    unknown = sorted(t for t in freq if not wordnet.synsets(t))
    print(f"\nTérminos que no están en el diccionario ({len(unknown)}):")
    print(textwrap.fill(", ".join(f"{t}({freq[t]})" for t in unknown), width=100))


if __name__ == "__main__":
    main()