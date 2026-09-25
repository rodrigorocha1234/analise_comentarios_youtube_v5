import logging
import sys
from src.servicos.orquestrador_pipeline import OrquestradorPipeline


def configurar_logging() -> None:
    """Configura formato de logs estruturados por etapa."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def executar_principal() -> None:
    """Ponto de entrada para execução completa do pipeline de agrupamento."""
    configurar_logging()
    logger = logging.getLogger("main")
    logger.info("Iniciando orquestração diária do projeto analise_comentarios_youtube.")

    orquestrador = OrquestradorPipeline(caminho_yaml="config/configuracao.yaml")
    sucesso = orquestrador.executar_pipeline()

    if sucesso:
        logger.info("Processamento diário concluído com êxito!")
    else:
        logger.warning("Pipeline executado sem gravação de novos dados ou com pendências.")


if __name__ == "__main__":
    executar_principal()
