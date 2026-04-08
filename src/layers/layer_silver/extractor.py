import json
from pathlib import Path

from sqlalchemy import text
import pandas as pd

from src.core.db import engine


def buscar_pendentes_df(): 

    query = "SELECT match_id, caminho FROM bronze_raw WHERE processado = 0"

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

def ler_json_achatado(match_id: str, caminho: str) -> pd.DataFrame:
    
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado:{caminho}")
    
    with open(arquivo, encoding="utf-8") as f:
        dados_brutos = json.load(f)
    
    df = pd.json_normalize(dados_brutos)

    df['match_id'] = match_id
    return df