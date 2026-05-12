from pathlib import Path
from sqlalchemy import create_engine
 
#Conexao com banco de dados
engine = create_engine("sqlite:///data/lol.db")
 
 #lista contendo as query que cria as tabela no sql
_SCHEMAS = [
    "src/layers/layer_bronze/schema_bronze.sql",
    "src/layers/layer_silver/schema_silver.sql"
]
 

# Abre o banco de dados e executa as query do sql
def inicializar_banco():
    with engine.begin() as conn:
        for arquivo in _SCHEMAS:
            sql = Path(arquivo).read_text(encoding="utf-8")
            conn.connection.executescript(sql)
 
inicializar_banco() 