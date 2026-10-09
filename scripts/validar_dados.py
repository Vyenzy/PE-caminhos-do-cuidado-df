"""Valida data/servicos.csv: protege a regra "nunca inventar dados".

Uso:  python scripts/validar_dados.py
Sai com código 1 se houver erros.
"""
import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "servicos.csv"
COLUNAS = [
    "id", "nome", "tipo", "regiao", "endereco", "telefone", "horario", "acesso",
    "publico", "fonte", "data_consulta", "status", "observacao", "tags",
]
STATUS_VALIDOS = {"verificado", "confirmar"}
TIPOS_VALIDOS = {
    "UBS", "CAPS", "CAPS III (24h)", "CAPS i (infantojuvenil)",
    "Ambulatório para adolescentes", "Urgência psiquiátrica",
    "Hospital Dia (IST/HIV e transexualidade)", "CAPS AD (álcool e drogas)",
    "CAPS AD III (24h)", "Atendimento a vítimas de violência",
}


def main() -> int:
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        if leitor.fieldnames != COLUNAS:
            print(f"ERRO: colunas diferentes do esperado.\n  esperado: {COLUNAS}\n  atual:    {leitor.fieldnames}")
            return 1
        linhas = list(leitor)

    erros, ids = [], set()
    for n, r in enumerate(linhas, start=2):  # linha 1 = cabeçalho
        rotulo = f"linha {n} ({r['id'] or 'sem id'})"
        if not r["id"]:
            erros.append(f"{rotulo}: id vazio")
        elif r["id"] in ids:
            erros.append(f"{rotulo}: id repetido")
        ids.add(r["id"])
        if r["status"] not in STATUS_VALIDOS:
            erros.append(f"{rotulo}: status deve ser {sorted(STATUS_VALIDOS)}")
        if r["tipo"] not in TIPOS_VALIDOS:
            erros.append(f"{rotulo}: tipo desconhecido '{r['tipo']}'")
        if not r["fonte"].strip():
            erros.append(f"{rotulo}: fonte vazia (sem fonte, não entra)")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["data_consulta"]):
            erros.append(f"{rotulo}: data_consulta deve ser AAAA-MM-DD")
        if r["status"] == "verificado" and "CONFIRMAR" in r["endereco"].upper():
            erros.append(f"{rotulo}: marcado 'verificado' mas o endereço ainda está a confirmar")
        if r["status"] == "verificado" and r["telefone"].strip().upper() == "A CONFIRMAR":
            erros.append(f"{rotulo}: marcado 'verificado' mas o telefone ainda está a confirmar")

    if erros:
        print("Problemas encontrados:")
        for e in erros:
            print(" -", e)
        return 1
    verificados = sum(r["status"] == "verificado" for r in linhas)
    print(f"OK: {len(linhas)} serviços ({verificados} verificados, {len(linhas) - verificados} a confirmar).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
