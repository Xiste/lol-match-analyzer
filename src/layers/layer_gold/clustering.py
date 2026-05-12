import logging
import pickle
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.layers.layer_gold.features import preparar_clustering, FEATURES_CLUSTERING

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

MODELS_DIR = Path("data/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

CAMINHO_KMEANS          = MODELS_DIR / "kmeans.pkl"
CAMINHO_SCALER_CLUSTER  = MODELS_DIR / "scaler_clustering.pkl"
CAMINHO_PERFIS          = MODELS_DIR / "perfil_clusters.csv"

# ---------------------------------------------------------------------------
# Rótulos automáticos por cluster
# Serão sobrescritos após o treino com base nos centróides reais
# ---------------------------------------------------------------------------

# Mapeamento de perfil baseado nas features dominantes de cada centróide
# A função _rotular_clusters() faz isso automaticamente.
ROTULOS_PADRAO = {
    0: ("🗡️ Carry",         "Alto dano, farm focado, pouca visão"),
    1: ("🛡️ Tanque/Frontline", "Absorve dano, aplica CC, sobrevive"),
    2: ("👁️ Suporte",       "Visão alta, CC alto, pouco dano"),
    3: ("🌀 Roamer/Jungler", "KP alto, CS médio, pressão no mapa"),
}


def _rotular_clusters(centros: pd.DataFrame) -> dict[int, tuple[str, str]]:
    """
    Atribui rótulos aos clusters com base nos centróides normalizados.
    Compara cada cluster com os demais para identificar o perfil dominante.
    """
    rotulos = {}
    usados  = set()

    # Critérios em ordem de prioridade
    criterios = [
        ("visao_por_minuto",   "👁️ Suporte/Visionário", "Alta visão por minuto, suporte de mapa"),
        ("tempo_cc_aplicado",  "🔒 Controlador de Área", "Muito CC aplicado, engage/peeling"),
        ("dpm",                "🗡️ Carry de Dano",       "Alto DPM, focado em eliminar inimigos"),
        ("cs",                 "🌾 Farmer",              "Farm elevado, foco em economia individual"),
        ("kp",                 "🤝 Team Player",         "Alta participação em kills do time"),
        ("solo_kills",         "⚔️ Duelista",            "Muitas kills solo, domínio 1v1"),
    ]

    # Para cada cluster, identifica qual feature ele lidera
    for cluster_id in centros.index:
        for feat, label, desc in criterios:
            if feat not in centros.columns:
                continue
            # Verifica se este cluster tem o maior valor nesta feature
            if centros[feat].idxmax() == cluster_id and label not in usados:
                rotulos[cluster_id] = (label, desc)
                usados.add(label)
                break
        else:
            rotulos[cluster_id] = (f"Grupo {cluster_id}", "Perfil misto")

    return rotulos


def treinar_clustering(n_clusters: int = 4) -> dict:
    """
    Treina o KMeans, salva os modelos e retorna os perfis encontrados.
    Retorna dict com: rotulos, perfil_medio, n_clusters
    """
    log.info("📦 Carregando dados para clustering...")
    df = preparar_clustering()

    if len(df) < n_clusters * 5:
        raise ValueError(
            f"Dados insuficientes: {len(df)} registros para {n_clusters} clusters. "
            "Adicione mais partidas ao banco."
        )

    log.info(f"📊 {len(df)} registros | {n_clusters} clusters")

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    df["cluster"] = kmeans.labels_

    # Perfil médio de cada cluster (valores originais, não normalizados)
    perfil = df.groupby("cluster")[FEATURES_CLUSTERING].mean().round(2)
    perfil["total_partidas"] = df.groupby("cluster").size()

    # Rotula automaticamente
    rotulos = _rotular_clusters(perfil)
    perfil["rotulo"] = [rotulos[i][0] for i in perfil.index]
    perfil["descricao"] = [rotulos[i][1] for i in perfil.index]

    # Salva tudo
    with open(CAMINHO_KMEANS, "wb") as f:
        pickle.dump(kmeans, f)
    with open(CAMINHO_SCALER_CLUSTER, "wb") as f:
        pickle.dump(scaler, f)

    perfil.to_csv(CAMINHO_PERFIS)

    log.info("✅ Clustering concluído!")
    log.info(f"\n{perfil[['rotulo', 'descricao', 'total_partidas']].to_string()}")

    return {
        "rotulos":      rotulos,
        "perfil_medio": perfil,
        "n_clusters":   n_clusters,
    }


def prever_cluster(df_input: pd.DataFrame) -> pd.Series:
    """
    Recebe um DataFrame com as FEATURES_CLUSTERING e retorna
    o cluster previsto para cada linha.
    """
    if not CAMINHO_KMEANS.exists() or not CAMINHO_SCALER_CLUSTER.exists():
        raise FileNotFoundError("Modelo de clustering não encontrado. Treine primeiro.")

    with open(CAMINHO_KMEANS, "rb") as f:
        kmeans = pickle.load(f)
    with open(CAMINHO_SCALER_CLUSTER, "rb") as f:
        scaler = pickle.load(f)

    cols_disponiveis = [c for c in FEATURES_CLUSTERING if c in df_input.columns]
    X = df_input[cols_disponiveis].fillna(0)
    X_scaled = scaler.transform(X)

    return pd.Series(kmeans.predict(X_scaled), index=df_input.index)


def carregar_perfis() -> pd.DataFrame:
    """Lê o CSV de perfis salvo após o treino."""
    if not CAMINHO_PERFIS.exists():
        return pd.DataFrame()
    return pd.read_csv(CAMINHO_PERFIS, index_col=0)


if __name__ == "__main__":
    treinar_clustering()