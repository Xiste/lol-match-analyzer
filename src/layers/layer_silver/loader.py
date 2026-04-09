from sqlalchemy import text
from enum import IntEnum


class StatusProcessamento(IntEnum):
    PENDENTE = 0
    SUCESSO  = 1
    ERRO     = 2

def salvar_players(conn, players: list[dict]) -> None:
    if not players:
        return
    
    conn.execute(
        text("""
            INSERT INTO jogadores (puuid, nick, tag, regiao)
            VALUES (:puuid, :nick, :tag, :regiao)
            ON CONFLICT(puuid) DO UPDATE SET
                nick    = excluded.nick,
                tag     = excluded.tag,
                regiao  = excluded.regiao
        """),
        players,      
    )

def salvar_partida(conn, partida: dict) -> None:
    conn.execute(
        text("""
            INSERT INTO partidas (match_id, data, duracao, modo, path)
            VALUES (:match_id, :data, :duracao, :modo, :path)
            ON CONFLICT(match_id) DO NOTHING
        """),
        partida,
    )

def salvar_desempenhos(conn, desempenhos: list[dict]) -> None:
    if not desempenhos:
        return
    
    conn.execute(
        text("DELETE FROM desempenho WHERE match_id = :match_id"),
        {"match_id": desempenhos[0]["match_id"]},
    )
    
    conn.execute(
        text("""
            INSERT INTO desempenho (
                match_id, puuid, campeao, posicao, vitoria,
                kills, deaths, assists,
                ouro, cs,
                dano_campeoes, dano_objetivos, dano_mitigado,
                dpm, kp, placar_visao
            ) VALUES (
                :match_id, :puuid, :campeao, :posicao, :vitoria,
                :kills, :deaths, :assists,
                :ouro, :cs,
                :dano_campeoes, :dano_objetivos, :dano_mitigado,
                :dpm, :kp, :placar_visao
            )
        """),
        desempenhos,
    )

def marcar_sucesso(conn, match_id: str) -> None:
    conn.execute(
        text("""
            UPDATE bronze_raw
            SET processado = 1, log = 'OK'
            WHERE match_id = :match_id
        """),
        {"match_id": match_id},
    )

def marcar_erro(conn, match_id: str, erro: str) -> None:
    conn.execute(
        text("""
            UPDATE bronze_raw
            SET processado = :status, log = :log
            WHERE match_id = :match_id
        """),
        {"status": StatusProcessamento.ERRO, "log": erro[:500], "match_id": match_id},
    )