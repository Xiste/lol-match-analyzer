import json
from pathlib import Path
from sqlalchemy import text

from src.core.db import engine


def buscar_pendentes(): 

    with engine.connect() as conn:
        registros = conn.execute(
            text("SELECT match_id, caminho FROM bronze_raw WHERE processado = 0")
        ).fetchall()
    return [(row.match_id, row.caminho) for row in registros]

def ler_json(match_id: str, caminho: str):
    
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado:{caminho}")
    
    try:
        with open(arquivo, encoding="utf-8") as f:
            return json.load(f)
            
    except json.JSONDecodeError as exc:
        raise ValueError(f"Partida {match_id}: O arquivo JSON está corrompido. Detalhe: {exc}")