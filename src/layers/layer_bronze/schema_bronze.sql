CREATE TABLE IF NOT EXISTS bronze_raw (
    match_id    TEXT PRIMARY KEY,
    caminho     TEXT,
    processado  INTEGER DEFAULT 0,  -- 0 = bruto, 1 = inserido nas tabelas
    log         TEXT                -- erro ou mensagem do processamento
); 

-- Índice para deixar a extração da Silver rápida
CREATE INDEX IF NOT EXISTS idx_bronze_processado ON bronze_raw (processado);