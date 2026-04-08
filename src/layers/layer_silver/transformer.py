def _minutos(duracao_segundos: int) -> float:
    segundos = max(duracao_segundos, 1)
    return segundos / 60.0

def _kills_do_time(participantes: list, team_id: int) -> int:
    return sum(p.get("kills",0) for p in participantes if p.get("teamId") == team_id)

def _calcular_kp(kills: int, assists: int, kills_time: int) -> float:
    if kills_time == 0:
        return 0.0;
    return round((kills+assists) / kills_time, 4)