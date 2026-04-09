import logging

from src.layers.layer_silver import extractor, transformer, loader
from src.core.db import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

def _processar_uma(match_id: str, caminho:str) -> None:
    
    dados = extractor.ler_json(match_id, caminho)

    partida, players, desempenhos = transformer.transformar(dados)

    with engine.begin() as conn:
        loader.salvar_players(conn, players)
        loader.salvar_partida(conn, partida)
        loader.salvar_desempenhos(conn, desempenhos)
        loader.marcar_sucesso(conn, match_id)
    
def processar_silver():
   
    pendentes = extractor.buscar_pendentes()

    if not pendentes:
        log.info("✅ Nenhuma partida nova para processar.")
        return

    log.info(f"🔄 {len(pendentes)} partida(s) para processar...")

    sucessos = erros = 0

    # Processa cada partida isoladamente — um erro não interrompe as demais.
    for match_id, caminho in pendentes:
            
        try:
            _processar_uma(match_id, caminho)
            log.info(f"  ✅ {match_id} processada com sucesso.")
            sucessos += 1

        except Exception as exc:
            # Registra o erro no banco para você inspecionar depois
            with engine.begin() as conn:
                loader.marcar_erro(conn, match_id, str(exc))
                
            log.error(f"  ❌ Falha na partida {match_id}")
            erros += 1

    log.info(f"🏁 Processamento Concluído — {sucessos} sucesso(s) | {erros} erro(s).")

if __name__ == "__main__":
    processar_silver()