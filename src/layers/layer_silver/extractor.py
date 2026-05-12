import json
from pathlib import Path
from sqlalchemy import text

from src.core.db import engine

#Verifica as partidas da bronze_layer que nao foram filtradas 
def buscar_pendentes(): 

    with engine.connect() as conn:
        #pega as partida que nao foram processadas e guarda em registros
        registros = conn.execute(
            text("SELECT match_id, caminho FROM bronze_raw WHERE processado = 0")
        ).fetchall()
    return [(row.match_id, row.caminho) for row in registros]



def ler_json(match_id: str, caminho: str):
    
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado:{caminho}")
    
    # abre o arquivo e converte o arquivo para python ler
    try:
        with open(arquivo, encoding="utf-8") as f:
            return json.load(f)
            
    except json.JSONDecodeError as exc:
        raise ValueError(f"Partida {match_id}: O arquivo JSON está corrompido. Detalhe: {exc}")