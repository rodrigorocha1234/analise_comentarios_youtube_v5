import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import pandas as pd

from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto
from src.coleta.coletor_youtube import ColetorYoutube
from src.dominio.comentario import Comentario

logger = logging.getLogger(__name__)


class ColetorComentario:
    """Coleta e versiona comentários principais de vídeos do YouTube."""

    def __init__(self, cliente_youtube: ColetorYoutube, armazenamento: ArmazenamentoObjeto) -> None:
        self.cliente_youtube = cliente_youtube
        self.armazenamento = armazenamento

    def calcular_hash(self, texto: str) -> str:
        """Gera hash SHA-256 do conteúdo textual para detecção de alterações."""
        return hashlib.sha256(texto.strip().encode("utf-8")).hexdigest()

    def obter_indice(self) -> Dict[str, Dict[str, str]]:
        """Recupera o índice de versão e hash dos comentários já processados."""
        caminho = "controle/comentarios_processados/indice_comentarios.json"
        if not self.armazenamento.objeto_existe(caminho):
            return {}
        try:
            conteudo = self.armazenamento.ler_objeto(caminho)
            dados = json.loads(conteudo.decode("utf-8"))
            if isinstance(dados, dict):
                resultado: Dict[str, Dict[str, str]] = {}
                for k, v in dados.items():
                    if isinstance(v, dict):
                        resultado[str(k)] = {str(ik): str(iv) for ik, iv in v.items()}
                return resultado
            return {}
        except Exception as erro:
            logger.warning("Erro ao carregar índice de comentários: %s", erro)
            return {}

    def salvar_indice(self, indice: Dict[str, Dict[str, str]]) -> bool:
        """Grava o índice atualizado de comentários no MinIO."""
        caminho = "controle/comentarios_processados/indice_comentarios.json"
        conteudo = json.dumps(indice, indent=2).encode("utf-8")
        return self.armazenamento.gravar_objeto(caminho, conteudo)

    def coletar_comentarios(self, ids_videos: List[str], coletar_todos: bool = True) -> List[Comentario]:
        """Coleta comentários principais dos vídeos com paginação e versionamento incremental."""
        data_coleta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        indice = self.obter_indice()
        comentarios_persistir: List[Comentario] = []

        for id_video in ids_videos:
            logger.info("Coletando comentários do vídeo: %s", id_video)
            token_pagina = ""
            while True:
                parametros = {
                    "part": "snippet",
                    "videoId": id_video,
                    "maxResults": "100",
                    "textFormat": "plainText",
                }
                if token_pagina:
                    parametros["pageToken"] = token_pagina

                try:
                    resposta = self.cliente_youtube.executar_requisicao("commentThreads", parametros)
                except Exception as erro:
                    logger.error("Erro ao consultar commentThreads para o vídeo %s: %s", id_video, erro)
                    break

                itens = resposta.get("items")
                if isinstance(itens, list):
                    for item in itens:
                        if not isinstance(item, dict):
                            continue
                        snippet_thread = item.get("snippet")
                        if not isinstance(snippet_thread, dict):
                            continue
                        top_comment = snippet_thread.get("topLevelComment")
                        if not isinstance(top_comment, dict):
                            continue
                        com_snippet = top_comment.get("snippet")
                        if not isinstance(com_snippet, dict):
                            continue

                        id_comentario = str(top_comment.get("id", ""))
                        texto = str(com_snippet.get("textDisplay", ""))
                        autor = str(com_snippet.get("authorDisplayName", ""))
                        data_pub = str(com_snippet.get("publishedAt", ""))
                        data_upd = str(com_snippet.get("updatedAt", ""))
                        id_canal = str(snippet_thread.get("channelId", ""))

                        hash_atual = self.calcular_hash(texto)
                        info_anterior = indice.get(id_comentario)

                        if info_anterior is None:
                            versao = 1
                            comentario = Comentario(
                                id_comentario=id_comentario,
                                id_video=id_video,
                                id_canal=id_canal,
                                id_comentario_pai="",
                                tipo="COMENTARIO",
                                texto=texto,
                                autor=autor,
                                data_publicacao=data_pub,
                                data_atualizacao_youtube=data_upd,
                                data_coleta=data_coleta,
                                hash_conteudo=hash_atual,
                                versao=versao,
                                ativo=True,
                            )
                            comentarios_persistir.append(comentario)
                            indice[id_comentario] = {"hash": hash_atual, "versao": str(versao)}
                        else:
                            hash_anterior = info_anterior.get("hash", "")
                            versao_anterior = int(info_anterior.get("versao", "1"))
                            if hash_atual != hash_anterior:
                                versao_nova = versao_anterior + 1
                                comentario = Comentario(
                                    id_comentario=id_comentario,
                                    id_video=id_video,
                                    id_canal=id_canal,
                                    id_comentario_pai="",
                                    tipo="COMENTARIO",
                                    texto=texto,
                                    autor=autor,
                                    data_publicacao=data_pub,
                                    data_atualizacao_youtube=data_upd,
                                    data_coleta=data_coleta,
                                    hash_conteudo=hash_atual,
                                    versao=versao_nova,
                                    ativo=True,
                                )
                                comentarios_persistir.append(comentario)
                                indice[id_comentario] = {"hash": hash_atual, "versao": str(versao_nova)}

                token_pagina = str(resposta.get("nextPageToken", ""))
                if not token_pagina or not coletar_todos:
                    break

        if comentarios_persistir:
            logger.info("Persistindo %d novos/atualizados comentários na camada Bronze.", len(comentarios_persistir))
            caminho_parquet = f"bronze/comentarios/data_coleta={data_coleta}/comentarios.parquet"
            df_comentarios = pd.DataFrame([c.para_dicionario() for c in comentarios_persistir])
            self.armazenamento.gravar_dataframe(caminho_parquet, df_comentarios)

        self.salvar_indice(indice)
        return comentarios_persistir
