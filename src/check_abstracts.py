import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

data = json.loads(Path("data/processed/abstracts.json").read_text(encoding="utf-8"))

for item in data:
    abstract = item["abstract"]
    name = item["file"][:25]
    if abstract is None:
        print(f"{name:<25} | SIN ABSTRACT")
    else:
        print(f"{name:<25} | {len(abstract):>5} | {abstract[:30]} [...] {abstract[-70:]}")