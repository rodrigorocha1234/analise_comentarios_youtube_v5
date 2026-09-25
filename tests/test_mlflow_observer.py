from unittest.mock import MagicMock, patch
import pytest

from src.dominio.evento_pipeline import EventoPipeline
from src.observadores.observador import Observador
from src.observadores.observador_mlflow import ObservadorMlflow
from src.observadores.publicador_evento import PublicadorEvento


class ObservadorMock(Observador):
    def __init__(self):
        self.eventos = []

    def notificar_evento(self, evento: EventoPipeline) -> bool:
        self.eventos.append(evento)
        return True


def test_publicador_evento_notifica_observadores():
    publicador = PublicadorEvento()
    obs1 = ObservadorMock()
    obs2 = ObservadorMock()

    publicador.registrar_observador(obs1)
    publicador.registrar_observador(obs2)

    publicador.publicar_evento("coleta_iniciada", {"data": "2026-09-24"})

    assert len(obs1.eventos) == 1
    assert obs1.eventos[0].nome_evento == "coleta_iniciada"
    assert obs1.eventos[0].obter_detalhe("data") == "2026-09-24"

    assert len(obs2.eventos) == 1


def test_observador_mlflow_trata_eventos():
    with patch("mlflow.set_tracking_uri"), patch("mlflow.set_experiment"), \
         patch("mlflow.start_run"), patch("mlflow.end_run"), \
         patch("mlflow.log_param"), patch("mlflow.log_metric"), patch("mlflow.set_tag"):

        obs_mlflow = ObservadorMlflow(tracking_uri="http://teste:5000", experimento="teste")

        evento_ini = EventoPipeline(
            nome_evento="treinamento_iniciado",
            data_hora="2026-09-24T12:00:00Z",
            detalhes={"algoritmo": "kmeans"},
        )
        sucesso = obs_mlflow.notificar_evento(evento_ini)
        assert sucesso is True

        evento_fim = EventoPipeline(
            nome_evento="avaliacao_concluida",
            data_hora="2026-09-24T12:05:00Z",
            detalhes={"silhouette": "0.45", "clusters": "5"},
        )
        sucesso_fim = obs_mlflow.notificar_evento(evento_fim)
        assert sucesso_fim is True
