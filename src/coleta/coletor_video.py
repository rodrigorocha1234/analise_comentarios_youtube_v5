import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set
import pandas as pd

from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto
from src.coleta.coletor_youtube import ColetorYoutube
from src.dominio.video import Video

logger = logging.getLogger(__name__)


class ColetorVideo:
    """Responsável pela descoberta incremental de vídeos sem duplicação."""

    def __init__(self, cliente_youtube: ColetorYoutube, armazenamento: ArmazenamentoObjeto) -> None:
        self.cliente_youtube = cliente_youtube
        self.armazenamento = armazenamento

    def obter_conhecidos(self) -> Set[str]:
        """Recupera o conjunto de IDs de vídeos previamente registrados no controle."""
        caminho_controle = "controle/videos_processados/videos_conhecidos.json"
        if not self.armazenamento.objeto_existe(caminho_controle):
            return set()
        try:
            conteudo = self.armazenamento.ler_objeto(caminho_controle)
            dados = json.loads(conteudo.decode("utf-8"))
            if isinstance(dados, list):
                return {str(item) for item in dados}
            return set()
        except Exception as erro:
            logger.warning("Falha ao ler controle de vídeos conhecidos: %s", erro)
            return set()

    def registrar_conhecidos(self, ids_totais: Set[str]) -> bool:
        """Atualiza a lista de IDs de vídeos conhecidos no controle do MinIO."""
        caminho_controle = "controle/videos_processados/videos_conhecidos.json"
        conteudo = json.dumps(sorted(list(ids_totais)), indent=2).encode("utf-8")
        return self.armazenamento.gravar_objeto(caminho_controle, conteudo)

    def extrair_itens(self, itens_brutos: List[object], data_coleta: str) -> List[Video]:
        """Converte itens retornados pela API em entidades Video."""
        videos: List[Video] = []
        for item in itens_brutos:
            if not isinstance(item, dict):
                continue
            id_info = item.get("id")
            snippet = item.get("snippet")
            stats = item.get("statistics")

            id_video = ""
            if isinstance(id_info, dict):
                id_video = str(id_info.get("videoId", ""))
            elif isinstance(id_info, str):
                id_video = id_info

            if not id_video or not isinstance(snippet, dict):
                continue

            id_canal = str(snippet.get("channelId", ""))
            titulo = str(snippet.get("title", ""))
            descricao = str(snippet.get("description", ""))
            data_pub = str(snippet.get("publishedAt", ""))

            views = 0
            likes = 0
            comentarios = 0
            if isinstance(stats, dict):
                views = int(stats.get("viewCount", 0))
                likes = int(stats.get("likeCount", 0))
                comentarios = int(stats.get("commentCount", 0))

            video = Video(
                id_video=id_video,
                id_canal=id_canal,
                titulo=titulo,
                descricao=descricao,
                data_publicacao=data_pub,
                data_coleta=data_coleta,
                total_visualizacoes=views,
                total_curtidas=likes,
                total_comentarios=comentarios,
            )
            videos.append(video)
        return videos

    def coletar_videos(self, canais: List[str], limite_por_canal: int = 20) -> List[str]:
        """Executa busca incremental de vídeos por canal e persiste apenas novos registros."""
        data_coleta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conhecidos = self.obter_conhecidos()
        novos_videos: List[Video] = []
        todos_ids_coletados: Set[str] = set(conhecidos)

        for canal_id in canais:
            logger.info("Consultando vídeos para o canal: %s", canal_id)
            parametros = {
                "part": "snippet",
                "channelId": canal_id,
                "maxResults": str(limite_por_canal),
                "order": "date",
                "type": "video",
            }
            try:
                resposta = self.cliente_youtube.executar_requisicao("search", parametros)
                itens = resposta.get("items")
                if isinstance(itens, list):
                    for item in itens:
                        if isinstance(item, dict):
                            id_info = item.get("id")
                            if isinstance(id_info, dict):
                                v_id = str(id_info.get("videoId", ""))
                                if v_id:
                                    todos_ids_coletados.add(v_id)
                                    if v_id not in conhecidos:
                                        videos_convertidos = self.extrair_itens([item], data_coleta)
                                        novos_videos.extend(videos_convertidos)
            except Exception as erro:
                logger.error("Erro ao coletar vídeos do canal %s: %s", canal_id, erro)

        if novos_videos:
            logger.info("Persistindo %d novos vídeos na camada Bronze.", len(novos_videos))
            caminho_parquet = f"bronze/videos/data_coleta={data_coleta}/videos.parquet"
            df_novos = pd.DataFrame([v.para_dicionario() for v in novos_videos])
            self.armazenamento.gravar_dataframe(caminho_parquet, df_novos)

        self.registrar_conhecidos(todos_ids_coletados)
        return sorted(list(todos_ids_coletados))
