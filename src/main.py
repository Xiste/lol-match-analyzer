import json
from sqlalchemy import text
from database import engine
import collector

def iniciar_ingestao_bruta(nick, tag):

    #Pegando a info do jogador
    print(f"Buscando dados de:{nick}#{tag}...")
    jogador = collector.get_jogador(nick,tag)
    puuid = jogador['puuid']

    #salvar no db(evitando duplicadas)
    print("Buscando IDs das partidas recentes...")
    lista_ids = collector.get_match_ids(puuid)

    #Abre a conexão e salva o dado bruto de cada partida
    with engine.begin() as conn:
        for match_id in lista_ids:
            print(f"Baixando e salvando partida bruta: {match_id}")
                
            # Puxa o dicionário completo da API da Riot
            dados_da_api = collector.get_detalhes_partida(match_id)
                
            # Transforma o dicionário em uma string (texto) para o SQLite
            json_em_texto = json.dumps(dados_da_api)

            # Salva na tabela partidas_raw
            # Usamos INSERT OR IGNORE para não dar erro se você rodar o script 2x
            conn.execute(
                text("INSERT OR IGNORE INTO partidas_raw (match_id, json_bruto) VALUES (:id, :json)"),
                {"id": match_id, "json": json_em_texto}
                )
    print("\n✅ Sucesso! Os dados brutos estão salvos no lol.db")

if __name__ == "__main__":
    # Coloque aqui o nick e a tag que você quer testar
    iniciar_ingestao_bruta("Xistê", "xiste")