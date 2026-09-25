import collections
from datetime import datetime, timezone
import numpy as np
import pytest

from src.dominio.agrupamento import Agrupamento
from src.dominio.documento_processado import DocumentoProcessado
from src.processamento.tratador_stopword import TratadorStopword
from src.topicos.associador_comentario import AssociadorComentario
from src.topicos.calculador_tendencia import CalculadorTendencia
from src.topicos.nomeador_topico import NomeadorTopico


def test_nomeador_topico_uma_palavra_com_acentos():
    tratador = TratadorStopword([])
    nomeador = NomeadorTopico(tratador)

    textos_cluster = [
        "A produção musical deste vídeo ficou incrível",
        "Excelente produção sonora",
        "A qualidade da produção é evidente",
    ]
    fundo = collections.Counter(["produção", "musical", "excelente", "qualidade", "vídeo"])

    topico = nomeador.nomear_topico(numero_cluster=1, textos_cluster=textos_cluster, palavras_fundo=fundo)

    # Exatamente UMA palavra
    assert " " not in topico.palavra_representativa.strip()
    assert topico.numero_cluster == 1
    # Preservação estrita de acento
    assert topico.palavra_representativa.lower() == "produção"


def test_associador_comentario_hierarquia():
    associador = AssociadorComentario()

    agr_pai = Agrupamento(
        id_documento="doc_pai",
        id_video="v1",
        id_canal="c1",
        id_comentario="com_1",
        id_comentario_pai="",
        tipo="COMENTARIO",
        numero_cluster=1,
        topico="produção",
        probabilidade=0.9,
        data_publicacao="2026-09-01T00:00:00Z",
        texto_original="Comentário do Pai",
        modelo="BERTopic",
        versao_modelo="1.0.0",
    )

    agr_resp = Agrupamento(
        id_documento="doc_filho",
        id_video="v1",
        id_canal="c1",
        id_comentario="resp_1",
        id_comentario_pai="com_1",
        tipo="RESPOSTA",
        numero_cluster=1,
        topico="produção",
        probabilidade=0.95,
        data_publicacao="2026-09-01T01:00:00Z",
        texto_original="Resposta ao Pai",
        modelo="BERTopic",
        versao_modelo="1.0.0",
    )

    hierarquia = associador.agrupar_hierarquia([agr_pai, agr_resp])
    assert "com_1" in hierarquia
    pai, respostas = hierarquia["com_1"]
    assert pai.id_comentario == "com_1"
    assert len(respostas) == 1
    assert respostas[0].id_comentario == "resp_1"


def test_calculador_tendencia_tres_escopos_e_janelas():
    calculador = CalculadorTendencia([1, 7, 30])

    data_base = "2026-09-24T12:00:00Z"

    docs: list[Agrupamento] = []
    # 5 comentários de tecnologia nos últimos dias
    for i in range(5):
        docs.append(
            Agrupamento(
                id_documento=f"d_{i}",
                id_video="v_tech",
                id_canal="c_tech",
                id_comentario=f"com_{i}",
                id_comentario_pai="",
                tipo="COMENTARIO",
                numero_cluster=2,
                topico="inovação",
                probabilidade=0.88,
                data_publicacao="2026-09-23T10:00:00Z",
                texto_original="Texto sobre inovação",
                modelo="KMeans",
                versao_modelo="1.0.0",
            )
        )

    tendencias = calculador.calcular_tendencias(docs, data_referencia="2026-09-24T12:00:00")
    assert len(tendencias) > 0

    escopos_encontrados = {t.escopo for t in tendencias}
    assert "video" in escopos_encontrados
    assert "canal" in escopos_encontrados
    assert "canal_video" in escopos_encontrados

    # Verifica janelas
    janelas_encontradas = {t.janela_dias for t in tendencias}
    assert 1 in janelas_encontradas
    assert 7 in janelas_encontradas
    assert 30 in janelas_encontradas

    # Verifica campos do score
    item = tendencias[0]
    assert item.topico == "inovação"
    assert item.score_tendencia >= 0.0
    assert item.posicao_ranking >= 1
