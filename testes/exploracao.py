# %%

import sys
sys.path.append("../src")
from collector import *

# %%

jogador = get_jogador("Xistê", "xiste")
print(jogador)

# %%

match_ids = get_match_ids(jogador["puuid"])
match_ids

# %%

detalhes = get_detalhes_partida(match_ids["match_id"][0])
detalhes
# %%

df_dados_partida = get_todas_partidas(jogador["puuid"])
df_dados_partida

# %%
