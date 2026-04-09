from pathlib import Path
 
BRONZE_DIR = Path("data/bronze")
BRONZE_DIR.mkdir(parents=True, exist_ok=True)
 
QUANTIDADE_PARTIDAS = 20
BASE_URL = "https://americas.api.riotgames.com"