import requests
import os
from dotenv import load_dotenv
from src.core.config import BASE_URL, QUANTIDADE_PARTIDAS

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
headers = {"X-Riot-Token": api_key}

# pegar url
def _get(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# funcao para pegar id do usuario
def get_puuid_conta(nick: str, tag:str):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{nick}/{tag}"
    conta = _get(url)
    
    return {
        "puuid": conta["puuid"],
        "nick": nick,
        "tag": tag,
    }

# puxa os id da partida pelo id do usuario
def get_match_ids(puuid: str):
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?count={QUANTIDADE_PARTIDAS}&start=0"
    return _get(url)

#pega os detalhes da partida
def get_detalhes_partida(match_id: str):
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    return _get(url)