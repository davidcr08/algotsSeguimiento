import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

term = sys.argv[1]
data = json.loads(Path("data/processed/abstracts.json").read_text(encoding="utf-8"))

for item in data:
    m = re.search(rf".{{0,60}}{re.escape(term)}.{{0,60}}", item["abstract"], re.I)
    if m:
        print(f"{item['file'][:25]:<25} | ...{m.group(0)}...")