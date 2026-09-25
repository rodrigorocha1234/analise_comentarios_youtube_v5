from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional
from src.armazenamento.adaptador_s3 import AdaptadorS3
from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.observadores.observador_mlflow import ObservadorMlflow
from src.observadores.publicador_evento import PublicadorEvento
from src.servicos.servico_agrupamento import ServicoAgrupamento
from src.servicos.servico_coleta import ServicoColeta
from src.servicos.servico_modelo import ServicoModelo
from src.servicos.servico_tendencia import ServicoTendencia

logger = logging.getLogger(__name__)


class OrquestradorPipeline:
    """Orquestrador central de ponta a ponta do ciclo diário de agrupamento e tendências."""

    def __init__(self, caminho_yaml: str = "config/configuracao.yaml") -> None:
        self.caminho_yaml = caminho_yaml
        self.configuracao = ConfiguracaoProjeto(caminho_yaml=caminho_yaml).carregar_configuracao()
        self.armazenamento = AdaptadorS3(bucket=self.configuracao.bucket_armazenamento)
        self.publicador = PublicadorEvento()
        self.observador_mlflow = ObservadorMlflow(experimento=self.configuracao.experimento_mlflow)
        self.publicador.registrar_observador(self.observador_mlflow)

        self.servico_coleta = ServicoColeta(self.configuracao, self.armazenamento, self.publicador)
        self.servico_agrupamento = ServicoAgrupamento(self.configuracao, self.armazenamento, self.publicador)
        self.servico_tendencia = ServicoTendencia(self.configuracao, self.armazenamento, self.publicador)
        self.servico_modelo = ServicoModelo(self.configuracao, self.publicador)

    def inicializar_componentes(self) -> bool:
        """Valida pré-requisitos de conectividade com MinIO e MLflow antes da execução."""
        logger.info("Validando componentes de infraestrutura...")
        self.armazenamento.garantir_bucket()
        return True

    def executar_pipeline(self) -> bool:
        """Executa o pipeline completo: coleta, spaCy, agrupadores, tendências e MLflow Serving."""
        self.inicializar_componentes()

        # 1. Coleta Bronze
        comentarios, respostas = self.servico_coleta.executar_coleta()

        if not comentarios and not respostas:
            data_hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            logger.info("Coleta sem itens novos. Carregando dados da camada Bronze...")
            comentarios, respostas = self.servico_coleta.carregar_bronze(data_hoje)

        if not comentarios and not respostas:
            logger.warning("Nenhum comentário ou resposta disponível para processamento nesta execução.")
            self.publicador.publicar_evento("execucao_concluida", {"motivo": "sem_dados"})
            return False

        # 2. Processamento spaCy, embeddings e agrupamento
        resultados_agrupamento = self.servico_agrupamento.executar_agrupamento(comentarios, respostas)

        # 3. Tendências e Nuvens de palavras (utiliza BERTopic ou o primeiro modelo disponível)
        modelo_referencia = "bertopic" if "bertopic" in resultados_agrupamento else next(iter(resultados_agrupamento.keys()))
        agrupamentos_ref, topicos_ref, _ = resultados_agrupamento[modelo_referencia]

        self.servico_tendencia.executar_tendencias(agrupamentos_ref)

        # 4. Registro no MLflow Serving
        self.servico_modelo.registrar_modelo(modelo_referencia, topicos_ref)

        # 5. Conclusão
        self.publicador.publicar_evento("execucao_concluida", {"modelo_principal": modelo_referencia})
        logger.info("Pipeline executado com sucesso de ponta a ponta.")
        return True
