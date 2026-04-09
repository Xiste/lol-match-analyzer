from pathlib import Path
from sqlalchemy import create_engine, text

Path("data").mkdir(exist_ok=True)

engine = create_engine("sqlite:///data/lol.db")

_schema = Path("src/sql/schema.sql").read_text(encoding="utf-8")
with engine.begin() as conn:
    conn.connection.executescript(_schema)