import pickle
import logging
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

from src.layers.layer_gold.features import preparar_classificador, FEATURES_CLASSIFICADOR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Onde os modelos serão salvos
MODELS_DIR = Path("data/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

CAMINHO_MODELO     = MODELS_DIR / "classificador.pkl"
CAMINHO_SCALER     = MODELS_DIR / "scaler_classificador.pkl"
CAMINHO_IMPORTANCIA = MODELS_DIR / "feature_importance.csv"


def treinar() -> None:
    """Treina o Random Forest e salva o modelo, scaler e feature importance."""

    log.info("📦 Carregando dados da Silver...")
    X, y = preparar_classificador()

    log.info(f"📊 Dataset: {len(X)} registros | {y.mean():.1%} de vitórias")

    # Divisão treino/teste (80/20) com estratificação para manter proporção de vitórias
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Normalização — importante para algumas features terem escalas muito diferentes
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    log.info("🌲 Treinando Random Forest...")
    modelo = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    modelo.fit(X_train_scaled, y_train)

    # Avaliação
    y_pred = modelo.predict(X_test_scaled)
    acuracia = accuracy_score(y_test, y_pred)
    log.info(f"✅ Acurácia no teste: {acuracia:.2%}")
    log.info(f"\n{classification_report(y_test, y_pred, target_names=['Derrota', 'Vitória'])}")

    # Salva modelo e scaler
    with open(CAMINHO_MODELO, "wb") as f:
        pickle.dump(modelo, f)
    with open(CAMINHO_SCALER, "wb") as f:
        pickle.dump(scaler, f)

    # Salva feature importance para análise
    importancia = pd.DataFrame({
        "feature":    FEATURES_CLASSIFICADOR,
        "importancia": modelo.feature_importances_,
    }).sort_values("importancia", ascending=False)

    importancia.to_csv(CAMINHO_IMPORTANCIA, index=False)

    log.info(f"💾 Modelo salvo em {CAMINHO_MODELO}")
    log.info("\n🔍 Top 10 features mais importantes:")
    log.info(importancia.head(10).to_string(index=False))


if __name__ == "__main__":
    treinar()