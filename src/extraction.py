import json
import re
from pathlib import Path

import fitz  # PyMuPDF

PDF_DIR = Path("data/pdfs")
OUT_FILE = Path("data/processed/abstracts.json")

# Marcadores donde suele terminar el abstract
END_MARKERS = r"(?:keywords?|index terms|(?:1|i)\.?\s+introduction|introduction)"


def read_first_pages(pdf_path: Path, n_pages: int = 2) -> str:
    with fitz.open(pdf_path) as doc:
        return "\n".join(doc[i].get_text() for i in range(min(n_pages, len(doc))))


def find_abstract(text: str) -> str | None:
    pattern = rf"abstract\s*[:\-—.]?\s*(.+?)(?=\n\s*{END_MARKERS}\b)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def main() -> None:
    results = []
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        abstract = find_abstract(read_first_pages(pdf))
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