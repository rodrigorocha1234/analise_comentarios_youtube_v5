import logging
import os
from typing import Dict, List, Optional
import mlflow
import mlflow.pyfunc
from mlflow.models import ModelSignature
from mlflow.types.schema import ColSpec, Schema
import pandas as pd
from dotenv import load_dotenv

from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.dominio.topico import Topico
from src.observadores.publicador_evento import PublicadorEvento
from src.servicos.modelo_inferencia import ModeloInferencia

logger = logging.getLogger(__name__)


class ServicoModelo:
    """Gerencia assinatura tipada, versionamento de schemas e publicação para MLflow Serving."""

    def __init__(
        self,
        configuracao: ConfiguracaoProjeto,
        publicador: PublicadorEvento,
    ) -> None:
        load_dotenv()
        self.configuracao = configuracao
        self.publicador = publicador
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.configuracao.experimento_mlflow)
        except Exception as erro:
            logger.warning("Falha ao inicializar MLflow para registro de modelo: %s", erro)

    def definir_assinatura(self) -> ModelSignature:
        """Cria assinatura explícita do contrato com versão de schemas de entrada e saída."""
        schema_entrada = Schema(
            [
                ColSpec("string", "texto"),
                ColSpec("string", "id_video"),
                ColSpec("string", "id_canal"),
            ]
        )
        schema_saida = Schema(
            [
                ColSpec("long", "numero_cluster"),
                ColSpec("string", "topico"),
                ColSpec("double", "probabilidade"),
            ]
        )
        return ModelSignature(inputs=schema_entrada, outputs=schema_saida)

    def preparar_serving(self, topicos: List[Topico]) -> ModeloInferencia:
        """Instancia o wrapper compatível com MLflow Serving a partir dos tópicos extraídos."""
        mapa: Dict[int, str] = {t.numero_cluster: t.palavra_representativa for t in topicos}
        return ModeloInferencia(
            mapa_topicos=mapa,
            versao_schema_entrada=self.configuracao.versao_schema_entrada,
            versao_schema_saida=self.configuracao.versao_schema_saida,
        )

    def registrar_modelo(
        self,
        nome_modelo: str,
        topicos: List[Topico],
    ) -> bool:
        """Registra o modelo selecionado no MLflow com exemplo e assinatura de schema versionada."""
        if not self.configuracao.registrar_modelos:
            logger.info("Registro de modelos desabilitado na configuração.")
            return False

        logger.info("Registrando modelo %s no MLflow Model Registry...", nome_modelo)
        modelo_wrapper = self.preparar_serving(topicos)
        assinatura = self.definir_assinatura()

        exemplo_entrada = pd.DataFrame(
            [
                {
                    "texto": "Essa produção ficou excelente, parabéns pelo vídeo!",
                    "id_video": "vid_exemplo_123",
                    "id_canal": "can_exemplo_456",
                }
            ]
        )

        try:
            nome_registro = f"{self.configuracao.nome_projeto}_{nome_modelo.lower()}"
            with mlflow.start_run(run_name=f"registro_{nome_modelo}"):
                mlflow.set_tag("schema_entrada", self.configuracao.versao_schema_entrada)
                mlflow.set_tag("schema_saida", self.configuracao.versao_schema_saida)
                mlflow.set_tag("modelo", nome_modelo)

                mlflow.pyfunc.log_model(
                    artifact_path="modelo",
                    python_model=modelo_wrapper,
                    signature=assinatura,
                    input_example=exemplo_entrada,
                    registered_model_name=nome_registro,
                )

            self.publicador.publicar_evento(
                "modelo_registrado",
                {
                    "modelo": nome_modelo,
                    "registro": nome_registro,
                    "schema_entrada": self.configuracao.versao_schema_entrada,
                    "schema_saida": self.configuracao.versao_schema_saida,
                },
            )
            logger.info("Modelo %s registrado com sucesso no MLflow Serving como %s.", nome_modelo, nome_registro)
            return True
        except Exception as erro:
            logger.warning("Falha ao registrar modelo no MLflow: %s", erro)
            return False
