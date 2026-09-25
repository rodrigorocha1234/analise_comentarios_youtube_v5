import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List
import pandas as pd

from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto
from src.coleta.coletor_youtube import ColetorYoutube
from src.dominio.comentario import Comentario
from src.dominio.resposta import Resposta

logger = logging.getLogger(__name__)


class ColetorResposta:
    """Coleta e versiona respostas aos comentários principais usando a YouTube Data API."""

    def __init__(self, cliente_youtube: ColetorYoutube, armazenamento: ArmazenamentoObjeto) -> None:
        self.cliente_youtube = cliente_youtube
        self.armazenamento = armazenamento

    def calcular_hash(self, texto: str) -> str:
        """Gera hash SHA-256 do conteúdo da resposta para controle de versão."""
        return hashlib.sha256(texto.strip().encode("utf-8")).hexdigest()

    def obter_indice(self) -> Dict[str, Dict[str, str]]:
        """Recupera o índice de versão e hash das respostas já gravadas."""
        caminho = "controle/respostas_processadas/indice_respostas.json"
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
            logger.warning("Erro ao carregar índice de respostas: %s", erro)
            return {}

    def salvar_indice(self, indice: Dict[str, Dict[str, str]]) -> bool:
        """Grava o índice atualizado de respostas no MinIO."""
        caminho = "controle/respostas_processadas/indice_respostas.json"
        conteudo = json.dumps(indice, indent=2).encode("utf-8")
        return self.armazenamento.gravar_objeto(caminho, conteudo)

    def coletar_respostas(self, comentarios_pais: List[Comentario]) -> List[Resposta]:
        """Consulta todas as respostas para cada comentário pai via endpoint comments."""
        data_coleta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        indice = self.obter_indice()
        respostas_persistir: List[Resposta] = []

        for pai in comentarios_pais:
            token_pagina = ""
            while True:
                parametros = {
                    "part": "snippet",
                    "parentId": pai.id_comentario,
                    "maxResults": "100",
                    "textFormat": "plainText",
                }
                if token_pagina:
                    parametros["pageToken"] = token_pagina

                try:
                    resposta_api = self.cliente_youtube.executar_requisicao("comments", parametros)
                except Exception as erro:
                    logger.debug("Comentário %s sem respostas adicionais ou erro: %s", pai.id_comentario, erro)
                    break

                itens = resposta_api.get("items")
                if isinstance(itens, list):
                    for item in itens:
                        if not isinstance(item, dict):
                            continue
                        snippet = item.get("snippet")
                        if not isinstance(snippet, dict):
                            continue

                        id_resposta = str(item.get("id", ""))
                        texto = str(snippet.get("textDisplay", ""))
                        autor = str(snippet.get("authorDisplayName", ""))
                        data_pub = str(snippet.get("publishedAt", ""))
                        data_upd = str(snippet.get("updatedAt", ""))

                        hash_atual = self.calcular_hash(texto)
                        info_anterior = indice.get(id_resposta)

                        if info_anterior is None:
                            versao = 1
                            resp = Resposta(
                                id_resposta=id_resposta,
                                id_comentario_pai=pai.id_comentario,
                                id_video=pai.id_video,
                                id_canal=pai.id_canal,
                                texto=texto,
                                autor=autor,
                                data_publicacao=data_pub,
                                data_atualizacao_youtube=data_upd,
                                data_coleta=data_coleta,
                                hash_conteudo=hash_atual,
                                versao=versao,
                                ativo=True,
                            )
                            respostas_persistir.append(resp)
                            indice[id_resposta] = {"hash": hash_atual, "versao": str(versao)}
                        else:
                            hash_anterior = info_anterior.get("hash", "")
                            versao_anterior = int(info_anterior.get("versao", "1"))
                            if hash_atual != hash_anterior:
                                versao_nova = versao_anterior + 1
                                resp = Resposta(
                                    id_resposta=id_resposta,
                                    id_comentario_pai=pai.id_comentario,
                                    id_video=pai.id_video,
                                    id_canal=pai.id_canal,
                                    texto=texto,
                                    autor=autor,
                                    data_publicacao=data_pub,
                                    data_atualizacao_youtube=data_upd,
                                    data_coleta=data_coleta,
                                    hash_conteudo=hash_atual,
                                    versao=versao_nova,
                                    ativo=True,
                                )
                                respostas_persistir.append(resp)
                                indice[id_resposta] = {"hash": hash_atual, "versao": str(versao_nova)}

                token_pagina = str(resposta_api.get("nextPageToken", ""))
                if not token_pagina:
                    break

        if respostas_persistir:
            logger.info("Persistindo %d respostas na camada Bronze.", len(respostas_persistir))
            caminho_parquet = f"bronze/respostas/data_coleta={data_coleta}/respostas.parquet"
            df_respostas = pd.DataFrame([r.para_dicionario() for r in respostas_persistir])
            self.armazenamento.gravar_dataframe(caminho_parquet, df_respostas)

        self.salvar_indice(indice)
        return respostas_persistir
