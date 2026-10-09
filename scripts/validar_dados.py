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
OPCIONAIS = {"lat", "lon"}  # posição aproximada para o mapa (opcional)
LAT_DF, LON_DF = (-16.1, -15.4), (-48.4, -47.2)  # caixa que contém o DF
STATUS_VALIDOS = {"verificado", "confirmar"}
TIPOS_VALIDOS = {
    "UBS", "CAPS", "CAPS III", "CAPS i (infantojuvenil)",
    "Ambulatório para adolescentes", "Urgência psiquiátrica",
    "Hospital Dia (IST/HIV e transexualidade)", "CAPS AD (álcool e drogas)",
    "CAPS AD III", "Atendimento a vítimas de violência",
    "Atendimento à mulher (CEAM e Casa da Mulher)", "CREAS (proteção social)",
}


def main() -> int:
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        campos = list(leitor.fieldnames or [])
        faltando = [c for c in COLUNAS if c not in campos]
        extras = [c for c in campos if c not in COLUNAS and c not in OPCIONAIS]
        if faltando or extras:
            print(f"ERRO: colunas diferentes do esperado.\n  faltando: {faltando}\n  extras:   {extras}")
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
        if "lat" in campos or "lon" in campos:
            la, lo = (r.get("lat") or "").strip(), (r.get("lon") or "").strip()
            if bool(la) != bool(lo):
                erros.append(f"{rotulo}: lat e lon devem vir juntas")
            elif la:
                try:
                    if not (LAT_DF[0] <= float(la) <= LAT_DF[1] and LON_DF[0] <= float(lo) <= LON_DF[1]):
                        erros.append(f"{rotulo}: lat/lon fora do Distrito Federal")
                except ValueError:
                    erros.append(f"{rotulo}: lat/lon não numéricos")
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
