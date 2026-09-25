import pandas as pd
import pytest

from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.dominio.topico import Topico
from src.observadores.publicador_evento import PublicadorEvento
from src.servicos.modelo_inferencia import ModeloInferencia
from src.servicos.servico_modelo import ServicoModelo


def test_assinatura_e_schemas_versionados():
    config = ConfiguracaoProjeto()
    publicador = PublicadorEvento()
    servico = ServicoModelo(config, publicador)

    assinatura = servico.definir_assinatura()
    assert assinatura.inputs is not None
    assert assinatura.outputs is not None

    nomes_inputs = [col.name for col in assinatura.inputs.inputs]
    assert "texto" in nomes_inputs
    assert "id_video" in nomes_inputs
    assert "id_canal" in nomes_inputs

    nomes_outputs = [col.name for col in assinatura.outputs.inputs]
    assert "numero_cluster" in nomes_outputs
    assert "topico" in nomes_outputs
    assert "probabilidade" in nomes_outputs


def test_modelo_inferencia_serving_predict():
    mapa_topicos = {0: "produção", 1: "culinária"}
    modelo = ModeloInferencia(mapa_topicos, "1.0.0", "1.0.0")

    dados_entrada = pd.DataFrame(
        [
            {"texto": "Comentário sobre áudio e vídeo", "id_video": "v1", "id_canal": "c1"},
            {"texto": "Receita maravilhosa de bolo", "id_video": "v2", "id_canal": "c2"},
        ]
    )

    saida = modelo.predict(context=None, model_input=dados_entrada)
    assert isinstance(saida, pd.DataFrame)
    assert len(saida) == 2
    assert "numero_cluster" in saida.columns
    assert "topico" in saida.columns
    assert "probabilidade" in saida.columns
