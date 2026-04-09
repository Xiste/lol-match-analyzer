from pathlib import Path
from sqlalchemy import create_engine
 
Path("data").mkdir(exist_ok=True)
 
engine = create_engine("sqlite:///data/lol.db")
 
_SCHEMAS = [
    "src/layers/layer_bronze/schema_bronze.sql",
    "src/layers/layer_silver/schema_silver.sql",
    "src/layers/layer_gold/schema_gold.sql",
]
 
def inicializar_banco() -> None:
    with engine.begin() as conn:
        for path in _SCHEMAS:
            sql = Path(path).read_text(encoding="utf-8")
            conn.connection.executescript(sql)
 
inicializar_banco() 