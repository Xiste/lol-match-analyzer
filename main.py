
# %%

from src.layers.layer_bronze.ingest_bronze import iniciar_ingestao_bruta

iniciar_ingestao_bruta("Lhama","cuspe")

# %%

from src.layers.layer_silver.pipeline import processar_silver

processar_silver()


# %%
