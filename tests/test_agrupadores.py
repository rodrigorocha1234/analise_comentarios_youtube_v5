import numpy as np
import pytest

from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.fabricas.fabrica_agrupador import FabricaAgrupador


@pytest.fixture
def embeddings_sinteticos():
    np.random.seed(42)
    # 3 grupos sintéticos com 10 amostras cada
    g1 = np.random.normal(loc=0.0, scale=0.1, size=(10, 300))
    g2 = np.random.normal(loc=5.0, scale=0.1, size=(10, 300))
    g3 = np.random.normal(loc=10.0, scale=0.1, size=(10, 300))
    return np.vstack([g1, g2, g3]).astype(np.float32)


def test_fabrica_listar_e_criar_todos_algoritmos(embeddings_sinteticos):
    config = ConfiguracaoProjeto()
    fabrica = FabricaAgrupador(config)
    algoritmos = fabrica.listar_disponiveis()
    assert len(algoritmos) == 12

    for nome in algoritmos:
        estrategia = fabrica.criar_modelo(nome)
        assert estrategia.obter_nome() is not None

        # Para BERTopic, precisamos passar textos
        textos = [f"Texto explicativo número {i}" for i in range(len(embeddings_sinteticos))]
        rotulos = estrategia.treinar_modelo(embeddings_sinteticos, textos=textos)

        assert isinstance(rotulos, np.ndarray)
        assert len(rotulos) == len(embeddings_sinteticos)

        probs = estrategia.obter_probabilidades()
        assert isinstance(probs, np.ndarray)
        assert len(probs) == len(embeddings_sinteticos)
