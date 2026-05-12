import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def _minutos(duracao_segundos: int) -> float:
    if duracao_segundos <= 0:
        raise ValueError(f"Duração inválida: {duracao_segundos}")
    return duracao_segundos / 60.0


def _calcular_kills_por_time(players: list) -> dict:
    kills_por_equipe = {}

    for player in players:
        id_da_equipe = player.get("teamId")
        if id_da_equipe:
            kills_atuais_da_equipe = kills_por_equipe.get(id_da_equipe, 0)
            kills_do_jogador = player.get("kills", 0)
            kills_por_equipe[id_da_equipe] = kills_atuais_da_equipe + kills_do_jogador

    return kills_por_equipe


def _calcular_kp(kills: int, assists: int, total_kills_da_equipe: int) -> float:
    if total_kills_da_equipe == 0:
        return 0.0
    return round((kills + assists) / total_kills_da_equipe * 100, 2)


def _extrair_posicao(player: dict) -> str:
    posicao_detectada = player.get("teamPosition") or player.get("individualPosition")
    if not posicao_detectada or posicao_detectada == "NONE":
        return "NONE"
    return "SUPPORT" if posicao_detectada == "UTILITY" else posicao_detectada


def _calcular_cs(player: dict) -> int:
    return player.get("totalMinionsKilled", 0) + player.get("neutralMinionsKilled", 0)


def _extrair_itens(player: dict) -> dict:
    return {
        "item_0": player.get("item0", 0),
        "item_1": player.get("item1", 0),
        "item_2": player.get("item2", 0),
        "item_3": player.get("item3", 0),
        "item_4": player.get("item4", 0),
        "item_5": player.get("item5", 0),
        "item_6": player.get("item6", 0),
    }


def _extrair_early_game(player: dict) -> dict:
    challenges = player.get("challenges", {})
    return {
        "cs_primeiros_10_min":  challenges.get("laneMinionsFirst10Minutes", 0),
        "gpm":                  round(challenges.get("goldPerMinute", 0.0), 2),
        "vantagem_cs_oponente": challenges.get("maxCsAdvantageOnLaneOpponent", 0),
    }


def _extrair_features_ml(player: dict) -> dict:
    """Extrai features avançadas voltadas para uso em modelos de ML."""
    challenges = player.get("challenges", {})
    return {
        # Early game avançado
        "vantagem_nivel_oponente": challenges.get("maxLevelLeadLaneOpponent", 0),
        "pratos_torre":            challenges.get("turretPlatesTaken", 0),

        # Combate
        "solo_kills":           challenges.get("soloKills", 0),
        "killing_sprees":       challenges.get("killingSprees", 0),
        "skillshots_acertados": challenges.get("skillshotsHit", 0),
        "skillshots_desviados": challenges.get("skillshotsDodged", 0),
        "tempo_cc_aplicado":    player.get("totalTimeCCDealt", 0),
        "tempo_morto":          player.get("totalTimeSpentDead", 0),
        "maior_tempo_vivo":     player.get("longestTimeSpentLiving", 0),
        "nivel_final":          player.get("champLevel", 0),

        # Visão
        "wards_colocadas":          challenges.get("stealthWardsPlaced", 0),
        "wards_controle_colocadas": challenges.get("controlWardsPlaced", 0),
        "visao_por_minuto":         round(challenges.get("visionScorePerMinute", 0.0), 4),

        # Participação no time
        "pct_dano_time":          round(challenges.get("teamDamagePercentage", 0.0), 4),
        "pct_dano_recebido_time": round(challenges.get("damageTakenOnTeamPercentage", 0.0), 4),

        # Filtro de qualidade
        "surrender": 1 if player.get("gameEndedInSurrender") else 0,
    }


def transformar_partida(dados: dict) -> dict:
    info_partida = dados.get("info", {})
    metadados_partida = dados.get("metadata", {})

    timestamp_ms = info_partida.get("gameCreation", 0)
    if timestamp_ms > 0:
        data_formatada = datetime.fromtimestamp(timestamp_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    else:
        data_formatada = "1970-01-01 00:00:00"

    duracao_segundos = info_partida.get("gameDuration", 0)
    minutos = duracao_segundos // 60
    segundos_restantes = duracao_segundos % 60
    duracao_formatada = f"{minutos}:{segundos_restantes:02d}"

    return {
        "match_id": metadados_partida.get("matchId", "ID_DESCONHECIDO"),
        "data":     data_formatada,
        "duracao":  duracao_formatada,
        "modo":     info_partida.get("gameMode", "DESCONHECIDO"),
        "path":     info_partida.get("gameVersion", "DESCONHECIDO"),
    }


def transformar_jogadores(players: list, match_id: str) -> list[dict]:
    if "_" not in match_id:
        raise ValueError(f"match_id com formato inesperado: {match_id!r}")
    regiao_partida = match_id.split("_")[0]

    lista_de_jogadores = []
    for player in players:
        nome_jogador = player.get("riotIdGameName") or player.get("summonerName") or "DESCONHECIDO"
        lista_de_jogadores.append({
            "puuid":  player.get("puuid", "PUUID_FALTANDO"),
            "nick":   nome_jogador,
            "tag":    player.get("riotIdTagline", ""),
            "regiao": regiao_partida,
        })

    return lista_de_jogadores


def transformar_desempenhos(players: list, match_id: str, duracao_seg: int) -> list[dict]:
    minutos_jogados = _minutos(duracao_seg)
    dicionario_kills_equipes = _calcular_kills_por_time(players)
    lista_desempenhos = []

    for player in players:
        id_da_equipe = player.get("teamId", 100)
        kills = player.get("kills", 0)
        assists = player.get("assists", 0)
        dano_a_campeoes = player.get("totalDamageDealtToChampions", 0)
        total_kills_da_equipe = dicionario_kills_equipes.get(id_da_equipe, 0)

        desempenho_base = {
            "match_id":          match_id,
            "puuid":             player.get("puuid", ""),
            "campeao":           player.get("championName", ""),
            "posicao":           _extrair_posicao(player),
            "vitoria":           1 if player.get("win") else 0,
            "kills":             kills,
            "deaths":            player.get("deaths", 0),
            "assists":           assists,
            "kp":                _calcular_kp(kills, assists, total_kills_da_equipe),
            "dano_campeoes":     dano_a_campeoes,
            "dpm":               round(dano_a_campeoes / minutos_jogados, 2),
            "dano_objetivos":    player.get("damageDealtToObjectives", 0),
            "dano_mitigado":     player.get("damageSelfMitigated", 0),
            "placar_visao":      player.get("visionScore", 0),
            "ouro":              player.get("goldEarned", 0),
            "cs":                _calcular_cs(player),
            "torres_destruidas": player.get("turretTakedowns", 0),
            "dragoes_abatidos":  player.get("dragonKills", 0),
            "first_blood_kill":  1 if player.get("firstBloodKill") else 0,
        }

        desempenho_base.update(_extrair_itens(player))
        desempenho_base.update(_extrair_early_game(player))
        desempenho_base.update(_extrair_features_ml(player))

        lista_desempenhos.append(desempenho_base)

    return lista_desempenhos


def transformar(dados: dict) -> tuple[dict, list[dict], list[dict]]:
    info_partida = dados.get("info", {})
    metadados_partida = dados.get("metadata", {})

    lista_players = info_partida.get("participants", [])
    duracao_segundos = info_partida.get("gameDuration", 0)
    match_id = metadados_partida.get("matchId", "ID_DESCONHECIDO")

    partida_limpa = transformar_partida(dados)
    jogadores_limpos = transformar_jogadores(lista_players, match_id)
    desempenhos_limpos = transformar_desempenhos(lista_players, match_id, duracao_segundos)

    return partida_limpa, jogadores_limpos, desempenhos_limpos