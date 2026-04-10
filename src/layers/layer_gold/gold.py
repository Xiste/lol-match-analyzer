import pandas as pd
from sqlalchemy import text
from src.core.db import engine


def get_puuid_por_nick(nick: str, tag: str) -> str | None:
    query = text("""
        SELECT puuid FROM jogadores
        WHERE LOWER(nick) = LOWER(:nick)
        AND LOWER(tag)  = LOWER(:tag)
    """)
    with engine.connect() as conn:
        resultado = conn.execute(query, {"nick": nick, "tag": tag}).fetchone()
    
    return resultado[0] if resultado else None


def get_resumo_jogador(puuid: str) -> pd.DataFrame:
    query = text("""
        SELECT
            j.nick,
            j.tag,
            j.regiao,
            COUNT(*)                        AS total_partidas,
            ROUND(AVG(d.vitoria) * 100, 1)  AS winrate,
            ROUND(AVG(d.kills), 2)          AS media_kills,
            ROUND(AVG(d.deaths), 2)         AS media_deaths,
            ROUND(AVG(d.assists), 2)        AS media_assists,
            ROUND(AVG(d.dpm), 0)            AS dpm_medio,
            ROUND(AVG(d.kp) * 100, 1)       AS kp_medio,
            ROUND(AVG(d.cs), 0)             AS cs_medio,
            ROUND(AVG(d.ouro), 0)           AS ouro_medio,
            ROUND(AVG(d.placar_visao), 1)   AS visao_media,

            MAX((d.kills + d.assists) * 1.0 / NULLIF(d.deaths, 0)) AS maior_kda,
            MIN((d.kills + d.assists) * 1.0 / NULLIF(d.deaths, 0)) AS menor_kda,
            MAX(d.deaths)                   AS maior_morte,
            MIN(d.deaths)                   AS menor_morte,
            MAX(d.dano_campeoes)            AS maior_dano,
            MIN(d.dano_campeoes)            AS menor_dano

        FROM jogadores j
        JOIN desempenho d ON j.puuid = d.puuid
        WHERE j.puuid = :puuid
        GROUP BY j.puuid
    """)
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn, params={"puuid": puuid})

def get_historico_partidas(puuid: str) -> pd.DataFrame:
    query = text("""
        SELECT
            p.data,
            p.modo,
            p.duracao,
            d.campeao,
            d.posicao,
            d.vitoria,
            d.kills,
            d.deaths,
            d.assists,
            d.kp,
            d.dpm,
            d.cs,
            d.ouro,
            d.dano_campeoes,
            d.dano_objetivos,
            d.dano_mitigado,
            d.placar_visao
        FROM desempenho d
        JOIN jogadores j ON d.puuid    = j.puuid
        JOIN partidas  p ON d.match_id = p.match_id
        WHERE d.puuid = :puuid
        ORDER BY p.data DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn, params={"puuid": puuid})


def get_desempenho_por_campeao(puuid: str) -> pd.DataFrame:
    query = text("""
        SELECT
            d.campeao,
            COUNT(*)                        AS partidas,
            ROUND(AVG(d.vitoria) * 100, 1)  AS winrate,
            ROUND(AVG(d.kills), 2)          AS media_kills,
            ROUND(AVG(d.deaths), 2)         AS media_deaths,
            ROUND(AVG(d.assists), 2)        AS media_assists,
            ROUND(AVG(d.dpm), 0)            AS dpm_medio,
            ROUND(AVG(d.cs), 0)             AS cs_medio,
            ROUND(AVG(d.ouro), 0)           AS ouro_medio
        FROM desempenho d
        WHERE d.puuid = :puuid
        GROUP BY d.campeao
        ORDER BY partidas DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn, params={"puuid": puuid})


def get_desempenho_por_posicao(puuid: str) -> pd.DataFrame:
    query = text("""
        SELECT
            d.posicao,
            COUNT(*)                        AS partidas,
            ROUND(AVG(d.vitoria) * 100, 1)  AS winrate,
            ROUND(AVG(d.kills), 2)          AS media_kills,
            ROUND(AVG(d.deaths), 2)         AS media_deaths,
            ROUND(AVG(d.assists), 2)        AS media_assists,
            ROUND(AVG(d.dpm), 0)            AS dpm_medio
        FROM desempenho d
        WHERE d.puuid = :puuid
        GROUP BY d.posicao
        ORDER BY partidas DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn, params={"puuid": puuid})