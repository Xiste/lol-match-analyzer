from sqlalchemy import text
from enum import IntEnum


class StatusProcessamento(IntEnum):
    PENDENTE = 0
    SUCESSO  = 1
    ERRO     = 2


# roda toda a lista de puuid de uma só vez — se o puuid já existir com nick/tag diferente, atualiza
def salvar_players(conn, players: list[dict]):
    if not players:
        return
    conn.execute(
        text("""
            INSERT INTO jogadores (puuid, nick, tag, regiao)
            VALUES (:puuid, :nick, :tag, :regiao)
            ON CONFLICT(puuid) DO UPDATE SET
                nick   = excluded.nick,
                tag    = excluded.tag,
                regiao = excluded.regiao
        """),
        players,
    )


def salvar_partida(conn, partida: dict):
    conn.execute(
        text("""
            INSERT INTO partidas (match_id, data, duracao, modo, path)
            VALUES (:match_id, :data, :duracao, :modo, :path)
            ON CONFLICT(match_id) DO NOTHING
        """),
        partida,
    )


# Delete/Insert garante que não haverá desempenhos duplicados se o script rodar mais de uma vez
def salvar_desempenhos(conn, desempenhos: list[dict]):
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
                dpm, kp, placar_visao,
                torres_destruidas, dragoes_abatidos, first_blood_kill,
                item_0, item_1, item_2, item_3, item_4, item_5, item_6,
                cs_primeiros_10_min, gpm, vantagem_cs_oponente,
                vantagem_nivel_oponente, pratos_torre,
                solo_kills, killing_sprees, skillshots_acertados, skillshots_desviados,
                tempo_cc_aplicado, tempo_morto, maior_tempo_vivo, nivel_final,
                wards_colocadas, wards_controle_colocadas, visao_por_minuto,
                pct_dano_time, pct_dano_recebido_time,
                surrender
            ) VALUES (
                :match_id, :puuid, :campeao, :posicao, :vitoria,
                :kills, :deaths, :assists,
                :ouro, :cs,
                :dano_campeoes, :dano_objetivos, :dano_mitigado,
                :dpm, :kp, :placar_visao,
                :torres_destruidas, :dragoes_abatidos, :first_blood_kill,
                :item_0, :item_1, :item_2, :item_3, :item_4, :item_5, :item_6,
                :cs_primeiros_10_min, :gpm, :vantagem_cs_oponente,
                :vantagem_nivel_oponente, :pratos_torre,
                :solo_kills, :killing_sprees, :skillshots_acertados, :skillshots_desviados,
                :tempo_cc_aplicado, :tempo_morto, :maior_tempo_vivo, :nivel_final,
                :wards_colocadas, :wards_controle_colocadas, :visao_por_minuto,
                :pct_dano_time, :pct_dano_recebido_time,
                :surrender
            )
        """),
        desempenhos,
    )


def marcar_sucesso(conn, match_id: str):
    conn.execute(
        text("""
            UPDATE bronze_raw
            SET processado = 1, log = 'OK'
            WHERE match_id = :match_id
        """),
        {"match_id": match_id},
    )


def marcar_erro(conn, match_id: str, erro: str):
    conn.execute(
        text("""
            UPDATE bronze_raw
            SET processado = :status, log = :log
            WHERE match_id = :match_id
        """),
        {"status": StatusProcessamento.ERRO, "log": erro[:500], "match_id": match_id},
    )