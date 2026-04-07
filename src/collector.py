import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
headers = {"X-Riot-Token": api_key}

BASE_URL = "https://americas.api.riotgames.com"
QUANTIDADE_PARTIDAS = 20

# pegar url
def get(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# funcao para pegar id do usuario
def get_jogador(nick, tag, regiao="br1"):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{nick}/{tag}"
    conta = get(url)
    return {
        "puuid": conta["puuid"],
        "nick": nick,
        "tag": tag,
    }

# puxa os id da partida pelo id do usuario
def get_match_ids(puuid):
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?count={QUANTIDADE_PARTIDAS}&start=0"
    return get(url)

#pega os detalhes da partida
def get_detalhes_partida(match_id):
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    return get(url)

#Extrai informacoes da partida pelo puuid do usuario
def extrair_dados(partida_json, puuid):
    info = partida_json["info"]

    jogador = next(p for p in info["participants"] if p["puuid"] == puuid)
    
    return {
        "match_id": partida_json["metadata"]["matchId"],
        "modo": info["gameMode"],
        "duracao": info["gameDuration"],
        "data": info["gameCreation"],
        "campeao": jogador["championName"],
        "kills": jogador["kills"],
        "deaths": jogador["deaths"],
        "assists": jogador["assists"],
        "dano_total": jogador["totalDamageDealtToChampions"],
        "ouro": jogador["goldEarned"],
        "vitoria": jogador["win"]
    } 

