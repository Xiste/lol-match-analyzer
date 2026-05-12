import pandas as pd
from sqlalchemy import text
from src.core.db import engine


# Colunas usadas como features nos dois modelos
FEATURES_CLASSIFICADOR = [
    "dpm", "kp", "cs", "gpm", "ouro",
    "dano_campeoes", "dano_objetivos", "dano_mitigado",
    "placar_visao", "visao_por_minuto",
    "torres_destruidas", "dragoes_abatidos", "first_blood_kill",
    "cs_primeiros_10_min", "vantagem_cs_oponente", "vantagem_nivel_oponente",
    "pratos_torre", "solo_kills", "killing_sprees",
    "skillshots_acertados", "skillshots_desviados",
    "tempo_cc_aplicado", "tempo_morto", "maior_tempo_vivo", "nivel_final",
    "wards_colocadas", "wards_controle_colocadas",
    "pct_dano_time", "pct_dano_recebido_time",
]

FEATURES_CLUSTERING = [
    "dpm", "kp", "cs", "gpm",
    "placar_visao", "visao_por_minuto",
    "solo_kills", "pct_dano_time", "pct_dano_recebido_time",
    "tempo_cc_aplicado", "wards_colocadas", "wards_controle_colocadas",
]

# Coluna alvo do classificador
TARGET = "vitoria"


def carregar_dataset() -> pd.DataFrame:
    """
    Lê todos os desempenhos da Silver, aplica filtros de qualidade
    e retorna o DataFrame bruto para ser usado nas funções abaixo.
    """
    query = text("""
        SELECT d.*, p.modo, p.duracao
        FROM desempenho d
        JOIN partidas p ON d.match_id = p.match_id
        WHERE d.surrender = 0
        AND p.modo = 'CLASSIC'
    """)
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    # Feature derivada: KDA ratio (não existe na API, calculamos aqui)
    df["kda_ratio"] = (df["kills"] + df["assists"]) / df["deaths"].replace(0, 1)

    return df


def preparar_classificador() -> tuple[pd.DataFrame, pd.Series]:
    """
    Retorna X (features) e y (target) prontos para treinar o classificador.
    Remove linhas com valores nulos nas features selecionadas.
    """
    df = carregar_dataset()

    df_limpo = df[FEATURES_CLASSIFICADOR + [TARGET]].dropna()

    X = df_limpo[FEATURES_CLASSIFICADOR]
    y = df_limpo[TARGET].astype(int)

    return X, y


def preparar_clustering() -> pd.DataFrame:
    """
    Retorna DataFrame com features de estilo de jogo para o KMeans.
    Remove linhas com valores nulos nas features selecionadas.
    """
    df = carregar_dataset()

    return df[FEATURES_CLUSTERING].dropna()