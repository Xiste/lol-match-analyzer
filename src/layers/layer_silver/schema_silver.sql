CREATE TABLE IF NOT EXISTS jogadores (
    puuid   TEXT PRIMARY KEY,
    nick    TEXT,
    tag     TEXT,
    regiao  TEXT    
);


CREATE TABLE IF NOT EXISTS partidas (
    match_id  TEXT PRIMARY KEY,
    data      TEXT,     -- formato: 'YYYY-MM-DD HH:MM:SS'
    duracao   TEXT,     -- formato: 'MM:SS'
    modo      TEXT,
    path      TEXT    
);


CREATE TABLE IF NOT EXISTS desempenho (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        TEXT REFERENCES partidas(match_id),
    puuid           TEXT REFERENCES jogadores(puuid),
    campeao         TEXT,
    posicao         TEXT,
    vitoria         INTEGER,    -- 1 = vitória, 0 = derrota  

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

    -- Métricas calculadas
    dpm             REAL,       -- dano por minuto
    kp              REAL,       -- participação em kills (0-100)
    placar_visao    INTEGER,

    -- Objetivos
    torres_destruidas   INTEGER,
    dragoes_abatidos    INTEGER,
    first_blood_kill    INTEGER,

    -- Itens (slots 0-6, incluindo trinket)
    item_0  INTEGER,
    item_1  INTEGER,
    item_2  INTEGER,
    item_3  INTEGER,
    item_4  INTEGER,
    item_5  INTEGER,
    item_6  INTEGER,

    
    cs_primeiros_10_min     INTEGER,    -- CS nos primeiros 10 min
    gpm                     REAL,       -- ouro por minuto
    vantagem_cs_oponente    INTEGER,    -- vantagem de CS sobre o oponente de rota

   
    vantagem_nivel_oponente INTEGER,    -- vantagem de nível sobre o oponente
    pratos_torre            INTEGER,    -- turret plates destruídas (pressão de early)

   
    solo_kills              INTEGER,    -- kills 1v1
    killing_sprees          INTEGER,    -- sequências de abate
    skillshots_acertados    INTEGER,    -- skillshots acertados
    skillshots_desviados    INTEGER,    -- skillshots desviados
    tempo_cc_aplicado       INTEGER,    -- tempo total de CC aplicado (segundos)
    tempo_morto             INTEGER,    -- tempo total passado morto (segundos)
    maior_tempo_vivo        INTEGER,    -- maior sequência sem morrer (segundos)
    nivel_final             INTEGER,    -- nível do campeão ao fim da partida

   
    wards_colocadas             INTEGER,    -- stealth wards colocadas
    wards_controle_colocadas    INTEGER,    -- control wards colocadas
    visao_por_minuto            REAL,       -- vision score por minuto

    
    pct_dano_time           REAL,       -- % do dano total da equipe
    pct_dano_recebido_time  REAL,       -- % do dano recebido da equipe

    
    surrender               INTEGER     -- 1 = partida encerrada por surrender
);