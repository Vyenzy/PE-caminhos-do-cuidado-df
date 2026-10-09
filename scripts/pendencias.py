"""Lista os serviços com status "confirmar" e o link da página oficial de cada um.

Uso:  python scripts/pendencias.py
"""
import csv
import re
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "servicos.csv"

with open(CSV_PATH, encoding="utf-8", newline="") as f:
    pendentes = [r for r in csv.DictReader(f) if r["status"] == "confirmar"]

print(f"{len(pendentes)} serviço(s) a confirmar:\n")
for r in sorted(pendentes, key=lambda r: (r["regiao"], r["nome"])):
    link = re.search(r"https?://\S+", r["observacao"])
    print(f"- [{r['id']}] {r['nome']} ({r['regiao']})")
    print(f"    {link.group(0) if link else '(sem link na observação)'}")
