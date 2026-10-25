import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

prefix = sys.argv[1]
pdf = next(Path("data/pdfs").glob(f"{prefix}. *.pdf"))

with pymupdf.open(pdf) as doc:
    print(pdf.name)
    print("-" * 60)
    print(doc[0].get_text()[:3000])