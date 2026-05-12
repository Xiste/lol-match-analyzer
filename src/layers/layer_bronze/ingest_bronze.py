from pathlib import Path
from datetime import datetime
import json

from sqlalchemy import text

from src.core.db import engine
import src.core.riot_cliente as riot_cliente
from src.core.config import BRONZE_DIR


def iniciar_ingestao_bruta(nick, tag):
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)  # cria a pasta se não existir

    print(f"🔍 Buscando dados de: {nick}#{tag}...")
    conta = riot_cliente.get_puuid_conta(nick, tag)

    print("📋 Buscando IDs das partidas recentes...")
    lista_ids = riot_cliente.get_match_ids(conta["puuid"])

    for match_id in lista_ids:
        caminho_arquivo = BRONZE_DIR / f"{match_id}.json"

        if caminho_arquivo.exists():
            print(f"⏩ {match_id} já existe. Pulando...")
            continue

        print(f"📥 Baixando: {match_id}")
        dados_da_api = riot_cliente.get_detalhes_partida(match_id)

        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_da_api, f, ensure_ascii=False, indent=4)

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT OR IGNORE INTO bronze_raw (match_id, caminho) 
                    VALUES (:id, :path)
                """),
                {"id": match_id, "path": str(caminho_arquivo)}
            )

        print(f"✅ {match_id} salva.")

    print(f"\n✅ Sucesso! JSONs em 'data/bronze/' e registros em '{engine.url.database}'")