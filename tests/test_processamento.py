import numpy as np
import pytest

from src.dominio.comentario import Comentario
from src.processamento.gerador_embedding import GeradorEmbedding
from src.processamento.processador_texto import ProcessadorTexto
from src.processamento.tratador_stopword import TratadorStopword


def test_stopwords_uniao_e_filtragem():
    tratador = TratadorStopword(["valeu", "show", "vídeo"])
    stops = tratador.obter_stopwords()
    assert "de" in stops
    assert "para" in stops
    assert "valeu" in stops
    assert "show" in stops
    assert "vídeo" in stops

    tokens = ["Essa", "produção", "foi", "show", "valeu"]
    filtrados = tratador.filtrar_tokens(tokens)
    assert "show" not in filtrados
    assert "valeu" not in filtrados
    assert "produção" in filtrados


def test_preservacao_acentos_unicode_e_limpeza():
    tratador = TratadorStopword([])
    processador = ProcessadorTexto(tratador, modelo_spacy="pt_core_news_sm")

    texto_com_url = "Veja mais em https://youtube.com/watch?v=123 e confira a produção musical e atenção aos detalhes!"
    limpo = processador.limpar_texto(texto_com_url)

    assert "https" not in limpo
    assert "produção" in limpo
    assert "atenção" in limpo
    # Garante que não foi mutilado para producao ou atencao
    assert "producao" not in limpo
    assert "atencao" not in limpo


def test_processamento_lote_documentos():
    tratador = TratadorStopword([])
    processador = ProcessadorTexto(tratador, modelo_spacy="pt_core_news_sm")

    c = Comentario(
        id_comentario="c1",
        id_video="v1",
        id_canal="can1",
        id_comentario_pai="",
        tipo="COMENTARIO",
        texto="Excelente explicação sobre algoritmos!",
        autor="Dev",
        data_publicacao="2026-09-01T12:00:00Z",
        data_atualizacao_youtube="2026-09-01T12:00:00Z",
        data_coleta="2026-09-01",
        hash_conteudo="hash1",
        versao=1,
        ativo=True,
    )

    docs = processador.processar_lote([c], [], tamanho_lote=10)
    assert len(docs) == 1
    assert docs[0].id_comentario == "c1"
    assert "explicação" in docs[0].texto_limpo
    assert docs[0].tipo == "COMENTARIO"


def test_gerador_embeddings_spacy():
    gerador = GeradorEmbedding(modelo_spacy="pt_core_news_md", lote_processamento=10)
    assert gerador.dimensao_vetor == 300

    textos = ["Comentário sobre inteligência artificial e aprendizado", "Música excelente e produção refinada"]
    embeddings = gerador.gerar_embeddings(textos)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 300)
    assert not np.all(embeddings == 0)
