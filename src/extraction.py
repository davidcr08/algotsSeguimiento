import json
import re
import unicodedata
from pathlib import Path

import pymupdf

PDF_DIR = Path("data/pdfs")
OUT_FILE = Path("data/processed/abstracts.json")

# "Abstract" también si viene con letras separadas (A B S T R A C T)
START = r"a\s*b\s*s\s*t\s*r\s*a\s*c\s*t"

# Marcadores donde suele terminar el abstract (incluye K E Y W O R D S)
END_MARKERS = (
    r"(?:k\s*e\s*y\s*w\s*o\s*r\s*d\s*s|key\s+words|index\s+terms"
    r"|article\s+history|(?:1|i)\.?\s+introduction|introduction)"
)

# Artículos sin marcador final: frase con la que empieza el texto que sigue al abstract
END_OVERRIDES = {
    "9.": "Since Alan Turing",
}

# Artículos con las keywords antes del abstract: se corta hasta esta frase (inclusive)
START_TRIMS = {
    "7.": "Ethical considerations",
}


def read_first_pages(pdf_path: Path, n_pages: int = 2) -> str:
    with pymupdf.open(pdf_path) as doc:
        return "\n".join(doc[i].get_text() for i in range(min(n_pages, len(doc))))


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # "ﬁ" -> "fi"
    text = re.sub(r"\u00ad\s*", "", text)  # guiones suaves: "tech\nnological"
    text = re.sub(r"([a-z])-\s*\n\s*([a-z])", r"\1\2", text)  # "cur-\nrent"
    return text


def find_abstract(
    text: str, end_phrase: str | None = None, start_trim: str | None = None
) -> str | None:
    text = clean_text(text)
    end = rf"\n\s*{END_MARKERS}\b"
    if end_phrase:
        phrase = r"\s+".join(re.escape(w) for w in end_phrase.split())
        end = rf"(?:{end}|{phrase})"
    pattern = rf"{START}\s*[:\-—.]?\s*(.+?)(?={end})"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    abstract = re.sub(r"\s+", " ", match.group(1)).strip()
    if start_trim:
        idx = abstract.find(start_trim)
        if idx != -1:
            abstract = abstract[idx + len(start_trim):].strip()
    return abstract


def main() -> None:
    results = []
    for pdf in sorted(PDF_DIR.rglob("*.pdf")):
        key = pdf.name.split(" ")[0]  # "9." -> prefijo numérico del archivo
        abstract = find_abstract(
            read_first_pages(pdf), END_OVERRIDES.get(key), START_TRIMS.get(key)
        )
        if abstract is None:
            print(f"[REVISAR] No se encontró abstract en: {pdf.name}")
        results.append(
            {"file": pdf.name, "title": None, "authors": None, "abstract": abstract}
        )

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ok = sum(1 for r in results if r["abstract"])
    print(f"{ok}/{len(results)} abstracts extraídos -> {OUT_FILE}")


if __name__ == "__main__":
    main()