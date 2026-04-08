from pathlib import Path
from datetime import datetime
import json

# 2. Bibliotecas de terceiros
from sqlalchemy import text

# 3. Módulos do próprio projeto
from src.core.db import engine
import src.core.riot_cliente as riot_cliente


BRONZE_DIR = Path("data/bronze")

def iniciar_ingestao_bruta(nick, tag):
    # Pegando a info do jogador
    print(f"🔍 Buscando dados de: {nick}#{tag}...")
    conta = riot_cliente.get_puuid_conta(nick, tag) # PUXANDO FUNCAO QUE EU CRIEI

    # Pegando IDs das partidas
    print("📋 Buscando IDs das partidas recentes...")
    lista_ids = riot_cliente.get_match_ids(conta["puuid"]) # PUXANDO FUNCAO QUE EU CRIEI

    # Abre a conexão e salva o dado bruto de cada partida
    with engine.begin() as conn:
        for match_id in lista_ids:
            caminho_arquivo = BRONZE_DIR / f"{match_id}.json"

            # 1. VERIFICA SE JÁ EXISTE (pula tudo, inclusive o banco)
            if caminho_arquivo.exists():
                print(f"⏩ {match_id} já existe. Pulando...")
                continue

            # 2. FAZ O DOWNLOAD
            print(f"📥 Baixando: {match_id}")
            dados_da_api = riot_cliente.get_detalhes_partida(match_id)

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_da_api, f, ensure_ascii=False, indent=4)

            # 3. REGISTRA NO BANCO SÓ APÓS SALVAR O ARQUIVO COM SUCESSO
            conn.execute(
                text("""
                    INSERT OR IGNORE INTO bronze_raw (match_id, caminho, data_coleta) 
                    VALUES (:id, :path, :data)
                """),
                {"id": match_id, "path": str(caminho_arquivo), "data": datetime.now().isoformat()}
            )
            
    print(f"\n✅ Sucesso! JSONs em 'data/bronze/' e registros em '{engine.url.database}'")

if __name__ == "__main__":
    iniciar_ingestao_bruta("Xistê", "xiste")