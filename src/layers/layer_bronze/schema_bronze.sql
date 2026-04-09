CREATE TABLE IF NOT EXISTS bronze_raw (
    match_id    TEXT PRIMARY KEY,
    caminho     TEXT,
    processado  INTEGER DEFAULT 0,  -- 0 = bruto, 1 = inserido nas tabelas
    log         TEXT,               -- erro ou mensagem do processamento
    data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
); 

-- Índice para deixar a extração da Silver super rápida
CREATE INDEX IF NOT EXISTS idx_bronze_processado ON bronze_raw (processado);