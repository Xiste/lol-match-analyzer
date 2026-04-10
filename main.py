# %%
from src.layers.layer_bronze.ingest_bronze import iniciar_ingestao_bruta
from src.layers.layer_silver.pipeline import processar_silver
from src.layers.layer_gold.gold import (
    get_puuid_por_nick,
    get_resumo_jogador,
    get_historico_partidas,
    get_desempenho_por_campeao,
    get_desempenho_por_posicao,
)

# %%
iniciar_ingestao_bruta("Xistê", "xiste")

# %%
processar_silver()

# %%
puuid = get_puuid_por_nick("Xistê", "xiste")
print(puuid)

# %%
df_resumo    = get_resumo_jogador(puuid)
df_historico = get_historico_partidas(puuid)
df_campeoes  = get_desempenho_por_campeao(puuid)
df_posicoes  = get_desempenho_por_posicao(puuid)

# %%
df_resumo

# %%
df_historico

# %%
df_campeoes

# %%
df_posicoes
# %%
