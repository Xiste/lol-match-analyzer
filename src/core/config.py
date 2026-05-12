from pathlib import Path
 
BRONZE_DIR = Path("data/bronze") # CAMINHO DA PASTA
BRONZE_DIR.mkdir(parents=True, exist_ok=True) # VERIFICA SE TEM A PASTA SE NAO VAI SER CRIADA
 
QUANTIDADE_PARTIDAS = 100 # QUANTIDADE DE PARTIDA QUE ELE VAI PUXAR
BASE_URL = "https://americas.api.riotgames.com"   ##URL PADRAO DA API