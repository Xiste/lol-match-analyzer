import pickle
import pandas as pd

# Carrega modelo e scaler
with open("data/models/classificador.pkl", "rb") as f:
    modelo = pickle.load(f)

with open("data/models/scaler_classificador.pkl", "rb") as f:
    scaler = pickle.load(f)

# Exemplo: dados de uma partida
dados = pd.DataFrame([{
    "dpm": 800,
    "kp": 60,
    "cs": 150,
    "gpm": 400,
    "ouro": 12000,
    "dano_campeoes": 20000,
    "dano_objetivos": 5000,
    "dano_mitigado": 8000,
    "placar_visao": 20,
    "visao_por_minuto": 0.8,
    "torres_destruidas": 2,
    "dragoes_abatidos": 1,
    "first_blood_kill": 0,
    "cs_primeiros_10_min": 70,
    "vantagem_cs_oponente": 15,
    "vantagem_nivel_oponente": 1,
    "pratos_torre": 3,
    "solo_kills": 2,
    "killing_sprees": 1,
    "skillshots_acertados": 30,
    "skillshots_desviados": 10,
    "tempo_cc_aplicado": 20,
    "tempo_morto": 30,
    "maior_tempo_vivo": 400,
    "nivel_final": 14,
    "wards_colocadas": 10,
    "wards_controle_colocadas": 3,
    "pct_dano_time": 0.30,
    "pct_dano_recebido_time": 0.20,
}])

X_scaled = scaler.transform(dados)
predicao = modelo.predict(X_scaled)
probabilidade = modelo.predict_proba(X_scaled)

print("Resultado previsto:", "Vitória 🏆" if predicao[0] == 1 else "Derrota 💀")
print(f"Confiança: {max(probabilidade[0]) * 100:.1f}%")