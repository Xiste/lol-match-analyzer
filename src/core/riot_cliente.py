import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
headers = {"X-Riot-Token": api_key}

BASE_URL = "https://americas.api.riotgames.com"
QUANTIDADE_PARTIDAS = 100


def _get(url, tentativas=3):
    for i in range(tentativas):
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"⏳ Rate limit atingido. Aguardando {retry_after}s...")
            time.sleep(retry_after + 1)
            continue

        response.raise_for_status()
        return response.json()

    raise Exception(f"Falha após {tentativas} tentativas: {url}")


def get_puuid_conta(nick: str, tag: str, regiao: str = "br1"):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{nick}/{tag}"
    conta = _get(url)

    return {
        "puuid": conta["puuid"],
        "nick": nick,
        "tag": tag,
    }


def get_match_ids(puuid: str):
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?count={QUANTIDADE_PARTIDAS}&start=0"
    return _get(url)


def get_detalhes_partida(match_id: str):
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    return _get(url)