CREATE TABLE IF NOT EXISTS jogadores (
    puuid   TEXT PRIMARY KEY,
    nick    TEXT,
    tag     TEXT,
    regiao  TEXT
);

CREATE TABLE IF NOT EXISTS partidas (
    match_id  TEXT PRIMARY KEY,
    data      INTEGER,
    duracao   INTEGER,
    modo      TEXT
);

CREATE TABLE IF NOT EXISTS desempenho (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id    TEXT REFERENCES partidas(match_id),
    puuid       TEXT REFERENCES jogadores(puuid),
    campeao     TEXT,
    kills       INTEGER,
    deaths      INTEGER,
    assists     INTEGER,
    dano_total  INTEGER,
    ouro        INTEGER,
    vitoria     BOOLEAN
);

CREATE TABLE IF NOT EXISTS partidas_raw (
    match_id TEXT PRIMARY KEY,
    json_bruto TEXT,  
    data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
);