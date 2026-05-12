import pickle
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from src.layers.layer_bronze.ingest_bronze import iniciar_ingestao_bruta
from src.layers.layer_silver.pipeline import processar_silver
from src.layers.layer_gold.features import FEATURES_CLASSIFICADOR, FEATURES_CLUSTERING
from src.layers.layer_gold.clustering import (
    prever_cluster,
    carregar_perfis,
    CAMINHO_KMEANS,
    CAMINHO_SCALER_CLUSTER,
)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
st.set_page_config(page_title="LoL Match Analyzer", layout="wide", page_icon="🎮")

CAMINHO_MODELO = Path("data/models/classificador.pkl")
CAMINHO_SCALER = Path("data/models/scaler_classificador.pkl")
CAMINHO_IMPORT = Path("data/models/feature_importance.csv")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _modelo_disponivel() -> bool:
    return CAMINHO_MODELO.exists() and CAMINHO_SCALER.exists()


def _cluster_disponivel() -> bool:
    return CAMINHO_KMEANS.exists() and CAMINHO_SCALER_CLUSTER.exists()


def _carregar_modelo():
    with open(CAMINHO_MODELO, "rb") as f:
        modelo = pickle.load(f)
    with open(CAMINHO_SCALER, "rb") as f:
        scaler = pickle.load(f)
    return modelo, scaler


def atualizar_dados(nick: str, tag: str) -> None:
    try:
        with st.spinner(f"Buscando as últimas 100 partidas de {nick}#{tag}..."):
            iniciar_ingestao_bruta(nick, tag)
            processar_silver()
        st.success(f"Dados de {nick} atualizados!")
        st.cache_data.clear()
    except Exception as exc:
        st.error(f"Erro ao atualizar: {exc}")


def treinar_modelo() -> None:
    try:
        with st.spinner("Treinando o classificador..."):
            from src.layers.layer_gold.classificador import treinar
            treinar()
        st.success("Classificador treinado!")
        st.cache_data.clear()
    except Exception as exc:
        st.error(f"Erro ao treinar classificador: {exc}")


def treinar_cluster() -> None:
    try:
        with st.spinner("Treinando o clustering..."):
            from src.layers.layer_gold.clustering import treinar_clustering
            treinar_clustering()
        st.success("Clustering treinado!")
        st.cache_data.clear()
    except Exception as exc:
        st.error(f"Erro ao treinar clustering: {exc}")


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

@st.cache_data
def carregar_dados_do_banco() -> pd.DataFrame:
    conn = sqlite3.connect("data/lol.db")
    try:
        query = """
            SELECT
                j.nick, j.puuid,
                d.campeao, d.posicao, d.vitoria,
                d.kills, d.deaths, d.assists, d.kp,
                d.dano_campeoes, d.dano_objetivos, d.dano_mitigado,
                d.dpm, d.ouro, d.cs, d.gpm,
                d.placar_visao, d.visao_por_minuto,
                d.torres_destruidas, d.dragoes_abatidos, d.first_blood_kill,
                d.cs_primeiros_10_min, d.vantagem_cs_oponente, d.vantagem_nivel_oponente,
                d.pratos_torre, d.solo_kills, d.killing_sprees,
                d.skillshots_acertados, d.skillshots_desviados,
                d.tempo_cc_aplicado, d.tempo_morto, d.maior_tempo_vivo, d.nivel_final,
                d.wards_colocadas, d.wards_controle_colocadas,
                d.pct_dano_time, d.pct_dano_recebido_time,
                d.surrender,
                p.data, p.duracao, p.modo
            FROM desempenho d
            JOIN jogadores j ON d.puuid = j.puuid
            JOIN partidas  p ON d.match_id = p.match_id
            ORDER BY p.data DESC
        """
        df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df


@st.cache_data
def carregar_feature_importance() -> pd.DataFrame:
    if not CAMINHO_IMPORT.exists():
        return pd.DataFrame()
    return pd.read_csv(CAMINHO_IMPORT)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("🔍 Buscar Jogador")
    nick_input = st.text_input("Nick", placeholder="Ex: Faker")
    tag_input  = st.text_input("Tag",  placeholder="Ex: KR1")

    if st.button("⬇️ Puxar Dados Recentes", use_container_width=True):
        if nick_input and tag_input:
            atualizar_dados(nick_input, tag_input)
        else:
            st.warning("Preencha Nick e Tag!")

    st.divider()
    st.header("🤖 Modelos Gold")

    if _modelo_disponivel():
        st.success("Classificador treinado ✅")
    else:
        st.warning("Classificador não treinado")
    if st.button("🌲 Treinar Classificador", use_container_width=True):
        treinar_modelo()

    st.markdown("")

    if _cluster_disponivel():
        st.success("Clustering treinado ✅")
    else:
        st.warning("Clustering não treinado")
    if st.button("🔵 Treinar Clustering", use_container_width=True):
        treinar_cluster()


# ---------------------------------------------------------------------------
# Dados principais
# ---------------------------------------------------------------------------

df = carregar_dados_do_banco()
st.title("🎮 LoL Match Analyzer")

if df.empty:
    st.info("Banco de dados vazio. Use a barra lateral para buscar um jogador.")
    st.stop()

lista_jogadores = df["nick"].unique().tolist()
jogador = st.sidebar.selectbox("Selecionar Jogador:", lista_jogadores)

df_jogador = df[df["nick"] == jogador].head(100).copy()
df_jogador["kda_ratio"] = (
    (df_jogador["kills"] + df_jogador["assists"])
    / df_jogador["deaths"].replace(0, 1)
)

# ===========================================================================
# ABAS
# ===========================================================================

aba_geral, aba_gold, aba_cluster, aba_importancia = st.tabs([
    "📊 Visão Geral",
    "🤖 Análise Gold (ML)",
    "🔵 Estilo de Jogo",
    "🔍 Feature Importance",
])

# ---------------------------------------------------------------------------
# ABA 1 — VISÃO GERAL
# ---------------------------------------------------------------------------

with aba_geral:
    st.header(f"📊 Histórico Recente — {jogador}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Partidas",  len(df_jogador))
    c2.metric("Winrate",   f"{df_jogador['vitoria'].mean() * 100:.0f}%")
    c3.metric("KDA Médio", f"{df_jogador['kda_ratio'].mean():.2f}")
    c4.metric("DPM Médio", f"{df_jogador['dpm'].mean():,.0f}")
    c5.metric("CS Médio",  f"{df_jogador['cs'].mean():.0f}")

    st.divider()

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("💀 Pior Partida (mortes)")
        pior      = df_jogador.loc[df_jogador["deaths"].idxmax()]
        resultado = "Vitória" if pior["vitoria"] == 1 else "Derrota"
        cor       = "orange" if pior["vitoria"] == 1 else "red"
        st.markdown(
            f"""<div style="padding:16px;border-radius:8px;border:2px solid {cor};">
                <b>{pior['campeao']}</b> — {resultado}<br>
                KDA: {int(pior['kills'])}/{int(pior['deaths'])}/{int(pior['assists'])}<br>
                Data: {pior['data'][:10]}
            </div>""",
            unsafe_allow_html=True,
        )

    with col_dir:
        st.subheader("🔥 Melhor Partida (dano)")
        melhor     = df_jogador.loc[df_jogador["dano_campeoes"].idxmax()]
        resultado2 = "Vitória" if melhor["vitoria"] == 1 else "Derrota"
        cor2       = "green"  if melhor["vitoria"] == 1 else "orange"
        st.markdown(
            f"""<div style="padding:16px;border-radius:8px;border:2px solid {cor2};">
                <b>{melhor['campeao']}</b> — {resultado2}<br>
                Dano: {int(melhor['dano_campeoes']):,} | DPM: {melhor['dpm']:,.0f}<br>
                Data: {melhor['data'][:10]}
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("KP% médio por Campeão")
        st.bar_chart(df_jogador.groupby("campeao")["kp"].mean().sort_values(ascending=True))
    with g2:
        st.subheader("DPM por Campeão")
        st.bar_chart(df_jogador.groupby("campeao")["dpm"].mean().sort_values(ascending=True))

    st.divider()
    st.subheader("📋 Histórico Completo")
    st.dataframe(
        df_jogador[["data","campeao","posicao","vitoria","kills","deaths","assists",
                    "kda_ratio","kp","dpm","cs","ouro","torres_destruidas","dragoes_abatidos"]]
        .rename(columns={
            "data":"Data","campeao":"Campeão","posicao":"Posição","vitoria":"Vitória",
            "kda_ratio":"KDA","kp":"KP%","cs":"CS","ouro":"Ouro",
            "torres_destruidas":"Torres","dragoes_abatidos":"Drags",
        }),
        use_container_width=True, hide_index=True,
    )

# ---------------------------------------------------------------------------
# ABA 2 — ANÁLISE GOLD (ML)
# ---------------------------------------------------------------------------

with aba_gold:
    st.header("🤖 Análise com Modelo de Machine Learning")

    if not _modelo_disponivel():
        st.warning("Modelo ainda não treinado. Use o botão na sidebar.")
        st.stop()

    modelo, scaler = _carregar_modelo()

    st.subheader(f"🎯 Probabilidade de Vitória — {jogador}")

    cols_faltando = [c for c in FEATURES_CLASSIFICADOR if c not in df_jogador.columns]
    if cols_faltando:
        st.error(f"Colunas ausentes: {cols_faltando}")
    else:
        df_pred = df_jogador[FEATURES_CLASSIFICADOR].dropna().copy()

        if df_pred.empty:
            st.warning("Dados insuficientes para o modelo.")
        else:
            X_scaled  = scaler.transform(df_pred)
            probs     = modelo.predict_proba(X_scaled)[:, 1]
            predicoes = modelo.predict(X_scaled)

            df_res = df_jogador.loc[df_pred.index, ["data","campeao","posicao","vitoria","kills","deaths","assists"]].copy()
            df_res["prob_vitoria"]    = (probs * 100).round(1)
            df_res["previsao_modelo"] = predicoes
            df_res["acertou"]         = (df_res["vitoria"] == df_res["previsao_modelo"]).astype(int)

            m1, m2, m3 = st.columns(3)
            m1.metric("Acurácia (neste jogador)",  f"{df_res['acertou'].mean() * 100:.1f}%")
            m2.metric("Prob. média nas Vitórias",  f"{df_res[df_res['vitoria']==1]['prob_vitoria'].mean():.1f}%")
            m3.metric("Prob. média nas Derrotas",  f"{df_res[df_res['vitoria']==0]['prob_vitoria'].mean():.1f}%")

            st.divider()
            st.subheader("📈 Probabilidade de Vitória por Partida")
            st.line_chart(df_res.reset_index(drop=True)["prob_vitoria"])

            st.divider()
            st.subheader("📋 Detalhes das Predições")
            st.dataframe(
                df_res[["data","campeao","posicao","kills","deaths","assists","vitoria","prob_vitoria","acertou"]]
                .rename(columns={
                    "data":"Data","campeao":"Campeão","posicao":"Posição","vitoria":"Real",
                    "prob_vitoria":"Prob. Vitória (%)","acertou":"Modelo Acertou",
                }),
                use_container_width=True, hide_index=True,
            )

    st.divider()
    st.subheader("🩺 Diagnóstico de Performance")

    vitorias = df_jogador[df_jogador["vitoria"] == 1]
    derrotas = df_jogador[df_jogador["vitoria"] == 0]

    for col, label, menor_melhor in [
        ("torres_destruidas", "Torres Destruídas",  False),
        ("pratos_torre",      "Pratos de Torre",    False),
        ("tempo_morto",       "Tempo Morto (seg)",  True),
        ("dano_objetivos",    "Dano a Objetivos",   False),
        ("gpm",               "Ouro por Minuto",    False),
    ]:
        if col not in df_jogador.columns:
            continue
        med_win  = vitorias[col].mean() if not vitorias.empty else 0
        med_loss = derrotas[col].mean() if not derrotas.empty else 0
        media    = df_jogador[col].mean()

        with st.expander(f"**{label}**"):
            d1, d2, d3 = st.columns(3)
            d1.metric("Sua Média Geral",    f"{media:.1f}")
            d2.metric("Média nas Vitórias", f"{med_win:.1f}")
            d3.metric("Média nas Derrotas", f"{med_loss:.1f}")
            if menor_melhor:
                if med_loss > med_win * 1.2:
                    st.error(f"⚠️ Você passa {((med_loss/max(med_win,0.01))-1)*100:.0f}% mais tempo morto nas derrotas.")
                else:
                    st.success("✅ Tempo morto bem controlado.")
            else:
                if med_win > med_loss * 1.1:
                    st.info(f"📌 Nas vitórias você performa {((med_win/max(med_loss,0.01))-1)*100:.0f}% melhor.")
                else:
                    st.success("✅ Performance consistente entre vitórias e derrotas.")

# ---------------------------------------------------------------------------
# ABA 3 — ESTILO DE JOGO (CLUSTERING)
# ---------------------------------------------------------------------------

with aba_cluster:
    st.header("🔵 Estilo de Jogo — Clustering")

    if not _cluster_disponivel():
        st.warning("Clustering não treinado. Use o botão '🔵 Treinar Clustering' na sidebar.")
        st.stop()

    df_perfis = carregar_perfis()

    if df_perfis.empty:
        st.error("Arquivo de perfis não encontrado. Retreine o clustering.")
        st.stop()

    # Prevê cluster de cada partida do jogador
    cols_cluster     = [c for c in FEATURES_CLUSTERING if c in df_jogador.columns]
    clusters_jogador = prever_cluster(df_jogador[cols_cluster].fillna(0))
    df_jogador["cluster"] = clusters_jogador.values

    # Cluster dominante
    cluster_dominante = int(df_jogador["cluster"].mode()[0])
    rotulo    = df_perfis.loc[cluster_dominante, "rotulo"]    if "rotulo"    in df_perfis.columns else f"Grupo {cluster_dominante}"
    descricao = df_perfis.loc[cluster_dominante, "descricao"] if "descricao" in df_perfis.columns else ""
    n_partidas_dominante = (df_jogador["cluster"] == cluster_dominante).sum()

    # --- Card do perfil ---
    st.markdown(f"""
    <div style="padding:24px;border-radius:12px;border:2px solid #4f8ef7;text-align:center;margin-bottom:16px;">
        <h2>{rotulo}</h2>
        <p style="font-size:1.1em;color:#aaa;">{descricao}</p>
        <p>Perfil identificado em <b>{n_partidas_dominante}</b> de <b>{len(df_jogador)}</b> partidas</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- Winrate por cluster ---
    st.subheader("🏆 Winrate por Estilo de Jogo")
    st.caption("Em qual modo de jogar você vence mais?")

    wr_cluster = (
        df_jogador.groupby("cluster")["vitoria"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "winrate", "count": "partidas"})
    )
    wr_cluster["winrate"] = (wr_cluster["winrate"] * 100).round(1)

    for cluster_id, row in wr_cluster.iterrows():
        perfil_label = (
            df_perfis.loc[cluster_id, "rotulo"]
            if "rotulo" in df_perfis.columns and cluster_id in df_perfis.index
            else f"Grupo {cluster_id}"
        )
        marcador = " ← seu perfil dominante" if cluster_id == cluster_dominante else ""
        col_a, col_b, col_c = st.columns([3, 1, 1])
        col_a.markdown(f"**{perfil_label}**{marcador}")
        col_b.metric("Winrate",  f"{row['winrate']:.0f}%")
        col_c.metric("Partidas", int(row["partidas"]))
        st.progress(row["winrate"] / 100)

    st.divider()

    # --- Evolução do estilo ao longo do tempo ---
    st.subheader("📈 Evolução do Estilo ao Longo das Partidas")
    st.caption("Cada valor é um cluster diferente — veja se seu estilo mudou com o tempo.")
    st.line_chart(df_jogador.reset_index(drop=True)["cluster"])

    st.divider()

    # --- Você vs média do seu cluster ---
    st.subheader(f"📊 Você vs Média do Perfil ({rotulo})")
    st.caption("Compara suas médias com o centróide do cluster dominante.")

    labels_amigaveis = {
        "dpm":                    "DPM",
        "kp":                     "Kill Participation (%)",
        "cs":                     "CS Total",
        "gpm":                    "Ouro por Minuto",
        "placar_visao":           "Vision Score",
        "visao_por_minuto":       "Visão por Minuto",
        "solo_kills":             "Solo Kills",
        "pct_dano_time":          "% Dano do Time",
        "pct_dano_recebido_time": "% Dano Recebido",
        "tempo_cc_aplicado":      "CC Aplicado (seg)",
        "wards_colocadas":        "Wards Colocadas",
        "wards_controle_colocadas": "Control Wards",
    }

    if cluster_dominante in df_perfis.index:
        perfil_ref = df_perfis.loc[cluster_dominante]
        linhas = []
        for feat in cols_cluster:
            media_jog = df_jogador[feat].mean()
            media_ref = float(perfil_ref.get(feat, 0))
            diff_pct  = ((media_jog / max(abs(media_ref), 0.01)) - 1) * 100
            linhas.append({
                "Métrica":         labels_amigaveis.get(feat, feat),
                "Você":            round(media_jog, 2),
                "Média do Perfil": round(media_ref, 2),
                "Diferença (%)":   f"{diff_pct:+.1f}%",
            })
        st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

    st.divider()

    # --- Perfil de todos os clusters ---
    st.subheader("🗂️ Perfil Médio de Cada Cluster")
    st.caption("Referência de como cada estilo se comporta nos dados gerais.")
    colunas_exibir = (["rotulo"] if "rotulo" in df_perfis.columns else []) + [c for c in cols_cluster if c in df_perfis.columns]
    st.dataframe(
        df_perfis[colunas_exibir].rename(columns={"rotulo": "Perfil"}),
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# ABA 4 — FEATURE IMPORTANCE
# ---------------------------------------------------------------------------

with aba_importancia:
    st.header("🔍 O que o Modelo Aprendeu?")

    df_imp = carregar_feature_importance()

    if df_imp.empty:
        st.warning("Treine o classificador primeiro.")
        st.stop()

    st.subheader("📊 Importância de cada Feature")
    st.bar_chart(df_imp.sort_values("importancia", ascending=True).set_index("feature")["importancia"])

    st.divider()

    explicacoes = {
        "torres_destruidas":        "Destruir torres é o maior indicador de vitória. Quem controla o mapa vence.",
        "pratos_torre":             "Pressão no early game. Quem destrói pratos ganha ouro e vantagem cedo.",
        "tempo_morto":              "Quanto mais tempo morto, menos você contribui. Sobreviver vale mais que kills.",
        "dano_objetivos":           "Participação em dragões e barão. Objetivos viram o jogo.",
        "gpm":                      "Ouro por minuto: eficiência geral de farm, kills e objetivos.",
        "dpm":                      "Dano por minuto. Pressão constante sobre o inimigo.",
        "cs":                       "Farm total. Base econômica do jogo.",
        "ouro":                     "Ouro total. Correlaciona com todos os aspectos da performance.",
        "dano_mitigado":            "Dano absorvido. Tanques que aguentam mais tendem a vencer.",
        "pct_dano_time":            "Sua fatia do dano do time.",
        "kp":                       "Kill participation. Estar presente nos abates do time.",
        "cs_primeiros_10_min":      "Farm nos primeiros 10 min. Dominância de lane no early.",
        "vantagem_cs_oponente":     "CS a mais que seu oponente de lane.",
        "solo_kills":               "Kills 1v1. Habilidade mecânica individual.",
        "placar_visao":             "Vision score. Controle de mapa e informação.",
        "visao_por_minuto":         "Vision score por minuto. Consistência na visão.",
        "wards_colocadas":          "Wards colocadas. Informação gerada para o time.",
        "wards_controle_colocadas": "Control wards. Remoção de visão inimiga.",
    }

    st.subheader("🏆 Top 5 Features")
    for _, row in df_imp.sort_values("importancia", ascending=False).head(5).iterrows():
        feat  = row["feature"]
        imp   = row["importancia"]
        texto = explicacoes.get(feat, "Feature relevante identificada pelo modelo.")
        st.markdown(f"**{feat}** — `{imp:.2%}` de importância  \n{texto}")
        st.progress(float(imp))

    st.divider()
    st.subheader("📋 Tabela Completa")
    st.dataframe(
        df_imp.sort_values("importancia", ascending=False)
        .rename(columns={"feature": "Feature", "importancia": "Importância"})
        .assign(Importância=lambda x: x["Importância"].map("{:.2%}".format)),
        use_container_width=True, hide_index=True,
    )