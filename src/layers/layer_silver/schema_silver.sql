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
    modo      TEXT,
    path    TEXT    
);

CREATE TABLE IF NOT EXISTS desempenho (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        TEXT REFERENCES partidas(match_id),
    puuid           TEXT REFERENCES jogadores(puuid),
    campeao         TEXT,
    posicao         TEXT,
    vitoria         BOOLEAN,  -- 1 para Vitória, 0 para Derrota
    
    -- KDA 
    kills           INTEGER,
    deaths          INTEGER,
    assists         INTEGER,
    
    -- Economia e Farm
    ouro            INTEGER,
    cs              INTEGER,  
    
    -- Combate e Dano
    dano_campeoes   INTEGER,  
    dano_objetivos  INTEGER,  
    dano_mitigado   INTEGER,  
    
    
    dpm             REAL,     --dano por minuto
    kp              REAL,     -- particao de kill
    placar_visao    INTEGER   
);