import logging
import os
from typing import Dict, Optional
import mlflow
from dotenv import load_dotenv

from src.dominio.evento_pipeline import EventoPipeline
from src.observadores.observador import Observador

logger = logging.getLogger(__name__)


class ObservadorMlflow(Observador):
    """Observador GoF responsável por registrar ciclo de vida, métricas e eventos no MLflow."""

    def __init__(self, tracking_uri: Optional[str] = None, experimento: str = "agrupamento_youtube") -> None:
        load_dotenv()
        self.tracking_uri: str = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.experimento: str = experimento
        self.run_ativa = False
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experimento)
            logger.info("MLflow configurado em %s com experimento %s", self.tracking_uri, self.experimento)
        except Exception as erro:
            logger.warning("Não foi possível conectar ao servidor MLflow em %s: %s", self.tracking_uri, erro)

    def iniciar_execucao(self, nome_run: str) -> bool:
        """Inicia uma nova run no MLflow finalizando qualquer run pendente."""
        try:
            if self.run_ativa:
                self.finalizar_execucao()
            mlflow.start_run(run_name=nome_run)
            self.run_ativa = True
            return True
        except Exception as erro:
            logger.warning("Falha ao iniciar run no MLflow: %s", erro)
            return False

    def finalizar_execucao(self) -> bool:
        """Finaliza a run atualmente ativa no MLflow."""
        try:
            if self.run_ativa:
                mlflow.end_run()
                self.run_ativa = False
                return True
            return False
        except Exception as erro:
            logger.warning("Falha ao finalizar run no MLflow: %s", erro)
            return False

    def registrar_metricas(self, metricas: Dict[str, float]) -> bool:
        """Registra métricas numéricas na run do MLflow."""
        try:
            if self.run_ativa:
                mlflow.log_metrics(metricas)
                return True
            return False
        except Exception as erro:
            logger.warning("Erro ao logar métricas no MLflow: %s", erro)
            return False

    def notificar_evento(self, evento: EventoPipeline) -> bool:
        """Processa eventos do pipeline traduzindo-os em ações de rastreamento no MLflow."""
        nome = evento.nome_evento
        detalhes = evento.detalhes

        try:
            if nome == "coleta_iniciada":
                self.iniciar_execucao("coleta_diaria")
                if self.run_ativa:
                    mlflow.set_tag("etapa", "coleta")
                    mlflow.set_tag("data_hora_inicio", evento.data_hora)

            elif nome == "coleta_concluida":
                if self.run_ativa:
                    for k, v in detalhes.items():
                        try:
                            mlflow.log_metric(f"coleta_{k}", float(v))
                        except (ValueError, TypeError):
                            mlflow.log_param(f"coleta_{k}", v)
                    self.finalizar_execucao()

            elif nome == "processamento_iniciado":
                self.iniciar_execucao("processamento_spacy")
                if self.run_ativa:
                    mlflow.set_tag("etapa", "processamento")

            elif nome == "processamento_concluido":
                if self.run_ativa:
                    for k, v in detalhes.items():
                        try:
                            mlflow.log_metric(f"proc_{k}", float(v))
                        except (ValueError, TypeError):
                            mlflow.log_param(f"proc_{k}", v)
                    self.finalizar_execucao()

            elif nome == "treinamento_iniciado":
                algoritmo = detalhes.get("algoritmo", "desconhecido")
                self.iniciar_execucao(f"agrupamento_{algoritmo}")
                if self.run_ativa:
                    mlflow.set_tag("algoritmo", algoritmo)
                    mlflow.log_param("algoritmo", algoritmo)

            elif nome == "avaliacao_concluida":
                if self.run_ativa:
                    for k, v in detalhes.items():
                        try:
                            mlflow.log_metric(k, float(v))
                        except (ValueError, TypeError):
                            mlflow.set_tag(k, v)
                    self.finalizar_execucao()

            elif nome == "tendencias_calculadas":
                self.iniciar_execucao("calculo_tendencias")
                if self.run_ativa:
                    for k, v in detalhes.items():
                        try:
                            mlflow.log_metric(f"tendencia_{k}", float(v))
                        except (ValueError, TypeError):
                            pass
                    self.finalizar_execucao()

            elif nome == "execucao_concluida":
                if self.run_ativa:
                    mlflow.set_tag("status", "sucesso")
                    self.finalizar_execucao()

            return True
        except Exception as erro:
            logger.warning("Erro no ObservadorMlflow ao processar evento %s: %s", nome, erro)
            return False
