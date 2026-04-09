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
    
    return round((kills+assists) / total_kills_da_equipe, 4)

def _extrair_posicao(player: dict) ->str:

    posicao_detectada =  player.get("teamPosition") or player.get("individualPosition")
    if not posicao_detectada or posicao_detectada == "NONE":
        return "NONE"
    return "SUPPORT" if posicao_detectada == "UTILITY" else posicao_detectada

def _calcular_cs(player: dict) -> int:

    minions_rota = player.get("totalMinionsKilled", 0)
    minions_selva = player.get("neutralMinionsKilled", 0)
    return minions_rota + minions_selva



def transformar_partida(dados: dict) -> dict:

    info_partida = dados.get("info", {})
    metadados_partida = dados.get("metadata", {})

    return {
        "match_id": metadados_partida.get("matchId", "ID_DESCONHECIDO"),
        "data": info_partida.get("gameCreation", 0),
        "duracao": info_partida.get("gameDuration", 0),
        "modo": info_partida.get("gameMode", "DESCONHECIDO"),
        "path": info_partida.get("gameVersion", "DESCONHECIDO")
    }

def transformar_jogadores(players: list, match_id: str) -> list[dict]:

    if "_" not in match_id:
        raise ValueError(f"match_id com formato inesperado: {match_id!r}")
    regiao_partida = match_id.split("_")[0]

    lista_de_jogadores = []

    for player in players:
        nome_jogador = player.get("riotIdGameName") or player.get("summonerName") or "DESCONHECIDO"
        lista_de_jogadores.append({
            "puuid": player.get("puuid", "PUUID_FALTANDO"),  
            "nick": nome_jogador,
            "tag": player.get("riotIdTagline", ""),
            "regiao": regiao_partida,
        })
    return lista_de_jogadores

def transformar_desempenhos(players: list, match_id: str, 
                            duracao_seg: int) -> list[dict]:
    minutos_jogados = _minutos(duracao_seg)
    dicionario_kills_equipes = _calcular_kills_por_time(players)
    lista_desempenhos = []

    for player in players: 
        id_da_equipe = player.get("teamId", 100)
        kills = player.get("kills", 0)
        assists = player.get("assists", 0)
        dano_a_campeoes = player.get("totalDamageDealtToChampions", 0)  #
        total_kills_da_equipe = dicionario_kills_equipes.get(id_da_equipe, 0)

        lista_desempenhos.append({
            "match_id":       match_id,
            "puuid":          player.get("puuid", ""),
            "campeao":        player.get("championName", ""),
            "posicao":        _extrair_posicao(player),
            "vitoria":        1 if player.get("win") else 0,
            "kills":          kills,
            "deaths":         player.get("deaths", 0),
            "assists":        assists,
            "kp":             _calcular_kp(kills, assists, total_kills_da_equipe),
            "dano_campeoes":  dano_a_campeoes,
            "dpm":            round(dano_a_campeoes / minutos_jogados, 2),
            "dano_objetivos": player.get("damageDealtToObjectives", 0),
            "dano_mitigado":  player.get("damageSelfMitigated", 0),
            "placar_visao":   player.get("visionScore", 0),
            "ouro":           player.get("goldEarned", 0),
            "cs":             _calcular_cs(player),
        })
    return lista_desempenhos





def transformar(dados: dict) -> tuple[dict, list[dict], list[dict]]:
    info_partida = dados.get("info",{})
    metadados_partida = dados.get("metadata",{})

    lista_players = info_partida.get("participants", [])
    duracao_segundos = info_partida.get("gameDuration", 0)
    match_id = metadados_partida.get("matchId", "ID_DESCONHECIDO")

    partida_limpa = transformar_partida(dados)
    jogadores_limpos = transformar_jogadores(lista_players, match_id)
    desempenhos_limpos = transformar_desempenhos(lista_players, match_id, duracao_segundos)

    return partida_limpa, jogadores_limpos, desempenhos_limpos