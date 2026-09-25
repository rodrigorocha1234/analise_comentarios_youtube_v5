import json
from unittest.mock import MagicMock
import pytest

from src.coleta.coletor_comentario import ColetorComentario
from src.coleta.coletor_resposta import ColetorResposta
from src.coleta.coletor_video import ColetorVideo
from src.coleta.coletor_youtube import ColetorYoutube
from src.dominio.comentario import Comentario


def test_descoberta_e_deduplicacao_de_videos():
    mock_yt = MagicMock(spec=ColetorYoutube)
    mock_arm = MagicMock()

    # Vídeo vid1 já conhecido
    mock_arm.objeto_existe.return_value = True
    mock_arm.ler_objeto.return_value = json.dumps(["vid1"]).encode("utf-8")

    # API retorna vid1 e vid2
    mock_yt.executar_requisicao.return_value = {
        "items": [
            {
                "id": {"videoId": "vid1"},
                "snippet": {
                    "channelId": "can1",
                    "title": "Video 1",
                    "description": "",
                    "publishedAt": "2026-09-01T00:00:00Z",
                },
                "statistics": {"viewCount": "100"},
            },
            {
                "id": {"videoId": "vid2"},
                "snippet": {
                    "channelId": "can1",
                    "title": "Video 2",
                    "description": "",
                    "publishedAt": "2026-09-02T00:00:00Z",
                },
                "statistics": {"viewCount": "200"},
            },
        ]
    }

    coletor = ColetorVideo(mock_yt, mock_arm)
    ids_totais = coletor.coletar_videos(["can1"])

    assert "vid1" in ids_totais
    assert "vid2" in ids_totais
    # Apenas vid2 deve ser gravado no parquet novo
    assert mock_arm.gravar_dataframe.called
    df_chamado = mock_arm.gravar_dataframe.call_args[0][1]
    assert len(df_chamado) == 1
    assert df_chamado.iloc[0]["id_video"] == "vid2"


def test_versionamento_comentarios_alteracao_e_nao_duplicacao():
    mock_yt = MagicMock(spec=ColetorYoutube)
    mock_arm = MagicMock()

    coletor = ColetorComentario(mock_yt, mock_arm)
    hash_orig = coletor.calcular_hash("Texto original")

    # Simula índice onde c1 já existe com hash original
    mock_arm.objeto_existe.return_value = True
    mock_arm.ler_objeto.return_value = json.dumps(
        {"c1": {"hash": hash_orig, "versao": "1"}}
    ).encode("utf-8")

    # Cenário 1: API retorna o mesmo texto (sem alteração) -> não persiste
    mock_yt.executar_requisicao.return_value = {
        "items": [
            {
                "snippet": {
                    "channelId": "can1",
                    "topLevelComment": {
                        "id": "c1",
                        "snippet": {
                            "textDisplay": "Texto original",
                            "authorDisplayName": "Autor",
                            "publishedAt": "2026-09-01T00:00:00Z",
                            "updatedAt": "2026-09-01T00:00:00Z",
                        },
                    },
                }
            }
        ]
    }

    comentarios_1 = coletor.coletar_comentarios(["v1"], coletar_todos=False)
    assert len(comentarios_1) == 0

    # Cenário 2: API retorna texto modificado -> cria versão 2
    mock_yt.executar_requisicao.return_value = {
        "items": [
            {
                "snippet": {
                    "channelId": "can1",
                    "topLevelComment": {
                        "id": "c1",
                        "snippet": {
                            "textDisplay": "Texto editado com nova informação",
                            "authorDisplayName": "Autor",
                            "publishedAt": "2026-09-01T00:00:00Z",
                            "updatedAt": "2026-09-02T00:00:00Z",
                        },
                    },
                }
            }
        ]
    }

    comentarios_2 = coletor.coletar_comentarios(["v1"], coletar_todos=False)
    assert len(comentarios_2) == 1
    assert comentarios_2[0].versao == 2
    assert comentarios_2[0].texto == "Texto editado com nova informação"


def test_coleta_respostas_e_relacionamento_com_pai():
    mock_yt = MagicMock(spec=ColetorYoutube)
    mock_arm = MagicMock()
    mock_arm.objeto_existe.return_value = False

    coletor_resp = ColetorResposta(mock_yt, mock_arm)

    pai = Comentario(
        id_comentario="com_pai_1",
        id_video="v1",
        id_canal="c1",
        id_comentario_pai="",
        tipo="COMENTARIO",
        texto="Comentário Pai",
        autor="Pai",
        data_publicacao="2026-09-01T00:00:00Z",
        data_atualizacao_youtube="2026-09-01T00:00:00Z",
        data_coleta="2026-09-01",
        hash_conteudo="abc",
        versao=1,
        ativo=True,
    )

    mock_yt.executar_requisicao.return_value = {
        "items": [
            {
                "id": "resp_1",
                "snippet": {
                    "textDisplay": "Primeira resposta",
                    "authorDisplayName": "Filho 1",
                    "publishedAt": "2026-09-01T01:00:00Z",
                    "updatedAt": "2026-09-01T01:00:00Z",
                },
            }
        ]
    }

    respostas = coletor_resp.coletar_respostas([pai])
    assert len(respostas) == 1
    assert respostas[0].id_comentario_pai == "com_pai_1"
    assert respostas[0].texto == "Primeira resposta"
    assert respostas[0].versao == 1
