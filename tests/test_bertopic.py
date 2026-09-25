import numpy as np
import pytest

from src.agrupadores.agrupador_bertopic import AgrupadorBertopic
from src.processamento.gerador_embedding import GeradorEmbedding


def test_bertopic_com_embeddings_spacy():
    gerador = GeradorEmbedding(modelo_spacy="pt_core_news_md")

    textos = [
        "A produção musical deste vídeo ficou incrível e muito profissional",
        "Qualidade de som e mixagem excelente na produção",
        "Áudio perfeito e produção espetacular",
        "Trilha sonora e masterização com alta produção técnica",
        "Gostei muito da gravação e edição de som deste vídeo",
        "Produção de áudio sensacional parabéns aos músicos",
        "A receita de bolo de cenoura com chocolate ficou ótima",
        "Adorei a receita do bolo e cobertura de chocolate",
        "Muito boa essa dica culinária para fazer bolo",
        "Receita de sobremesa deliciosa com massa de bolo fofinha",
        "Como preparar calda de chocolate para bolo caseiro",
        "Excelente doce e sobremesa fácil de fazer em casa",
    ]

    embeddings = gerador.gerar_embeddings(textos)
    assert embeddings.shape == (12, 300)

    agrupador = AgrupadorBertopic(
        top_n_words=5,
        min_cluster_size=2,
        min_samples=1,
        ngram_min=1,
        ngram_max=2,
        min_df=1,
    )

    rotulos = agrupador.treinar_modelo(embeddings, textos=textos)
    assert isinstance(rotulos, np.ndarray)
    assert len(rotulos) == len(textos)

    probs = agrupador.obter_probabilidades()
    assert len(probs) == len(textos)

    topicos = agrupador.obter_topicos()
    assert isinstance(topicos, dict)
