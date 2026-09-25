from datetime import datetime, timezone
import logging
from typing import Dict, List, Tuple
import pandas as pd

from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto
from src.coleta.coletor_comentario import ColetorComentario
from src.coleta.coletor_resposta import ColetorResposta
from src.coleta.coletor_video import ColetorVideo
from src.coleta.coletor_youtube import ColetorYoutube
from src.dominio.canal import Canal
from src.dominio.comentario import Comentario
from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.dominio.resposta import Resposta
from src.observadores.publicador_evento import PublicadorEvento

logger = logging.getLogger(__name__)


class ServicoColeta:
    """Orquestrador do processo diário de coleta incremental e persistência na camada Bronze."""

    def __init__(
        self,
        configuracao: ConfiguracaoProjeto,
        armazenamento: ArmazenamentoObjeto,
        publicador: PublicadorEvento,
    ) -> None:
        self.configuracao = configuracao
        self.armazenamento = armazenamento
        self.publicador = publicador
        self.cliente_youtube = ColetorYoutube()
        self.coletor_video = ColetorVideo(self.cliente_youtube, self.armazenamento)
        self.coletor_comentario = ColetorComentario(self.cliente_youtube, self.armazenamento)
        self.coletor_resposta = ColetorResposta(self.cliente_youtube, self.armazenamento)

    def obter_publicador(self) -> PublicadorEvento:
        """Retorna o publicador de eventos GoF Observer."""
        return self.publicador

    def carregar_bronze(
        self, data_coleta: str
    ) -> Tuple[List[Comentario], List[Resposta]]:
        """Lê os comentários e respostas gravados na camada Bronze para a data indicada."""
        caminho_com = f"bronze/comentarios/data_coleta={data_coleta}/comentarios.parquet"
        caminho_resp = f"bronze/respostas/data_coleta={data_coleta}/respostas.parquet"

        if not self.armazenamento.objeto_existe(caminho_com):
            objs = self.armazenamento.listar_objetos("bronze/comentarios/")
            parquets = sorted([o for o in objs if o.endswith(".parquet")])
            if parquets:
                caminho_com = parquets[-1]

        if not self.armazenamento.objeto_existe(caminho_resp):
            objs_r = self.armazenamento.listar_objetos("bronze/respostas/")
            parquets_r = sorted([o for o in objs_r if o.endswith(".parquet")])
            if parquets_r:
                caminho_resp = parquets_r[-1]

        comentarios: List[Comentario] = []
        respostas: List[Resposta] = []

        if self.armazenamento.objeto_existe(caminho_com):
            df_com = self.armazenamento.ler_dataframe(caminho_com)
            for _, linha in df_com.iterrows():
                comentarios.append(
                    Comentario(
                        id_comentario=str(linha.get("id_comentario", "")),
                        id_video=str(linha.get("id_video", "")),
                        id_canal=str(linha.get("id_canal", "")),
                        id_comentario_pai=str(linha.get("id_comentario_pai", "")),
                        tipo=str(linha.get("tipo", "COMENTARIO")),
                        texto=str(linha.get("texto", "")),
                        autor=str(linha.get("autor", "")),
                        data_publicacao=str(linha.get("data_publicacao", "")),
                        data_atualizacao_youtube=str(linha.get("data_atualizacao_youtube", "")),
                        data_coleta=str(linha.get("data_coleta", "")),
                        hash_conteudo=str(linha.get("hash_conteudo", "")),
                        versao=int(linha.get("versao", 1)),
                        ativo=str(linha.get("ativo", "true")).lower() == "true",
                    )
                )

        if self.armazenamento.objeto_existe(caminho_resp):
            df_resp = self.armazenamento.ler_dataframe(caminho_resp)
            for _, linha in df_resp.iterrows():
                respostas.append(
                    Resposta(
                        id_resposta=str(linha.get("id_resposta", "")),
                        id_comentario_pai=str(linha.get("id_comentario_pai", "")),
                        id_video=str(linha.get("id_video", "")),
                        id_canal=str(linha.get("id_canal", "")),
                        texto=str(linha.get("texto", "")),
                        autor=str(linha.get("autor", "")),
                        data_publicacao=str(linha.get("data_publicacao", "")),
                        data_atualizacao_youtube=str(linha.get("data_atualizacao_youtube", "")),
                        data_coleta=str(linha.get("data_coleta", "")),
                        hash_conteudo=str(linha.get("hash_conteudo", "")),
                        versao=int(linha.get("versao", 1)),
                        ativo=str(linha.get("ativo", "true")).lower() == "true",
                    )
                )

        return comentarios, respostas

    def executar_coleta(self) -> Tuple[List[Comentario], List[Resposta]]:
        """Executa a coleta diária completa publicando eventos para os observadores."""
        data_coleta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info("Iniciando coleta diária do YouTube para a data %s.", data_coleta)
        self.publicador.publicar_evento("coleta_iniciada", {"data_coleta": data_coleta})

        canais = self.configuracao.canais_alvo
        videos_diretos = self.configuracao.videos_alvo

        # 1. Coleta metadados dos canais e persiste na Bronze
        canais_persistir: List[Canal] = []
        for c_id in canais:
            c = Canal(
                id_canal=c_id,
                titulo=f"Canal {c_id}",
                descricao="",
                data_coleta=data_coleta,
            )
            canais_persistir.append(c)

        if canais_persistir:
            caminho_canais = f"bronze/canais/data_coleta={data_coleta}/canais.parquet"
            df_canais = pd.DataFrame([c.para_dicionario() for c in canais_persistir])
            self.armazenamento.gravar_dataframe(caminho_canais, df_canais)

        # 2. Descoberta incremental de vídeos
        ids_videos: List[str] = []
        if canais:
            ids_videos = self.coletor_video.coletar_videos(
                canais, limite_por_canal=self.configuracao.maximo_videos_canal
            )
        if videos_diretos:
            ids_videos = sorted(list(set(ids_videos) | set(videos_diretos)))

        logger.info("Total de vídeos a sincronizar comentários: %d", len(ids_videos))

        # 3. Sincronização incremental de comentários principais
        comentarios_novos = self.coletor_comentario.coletar_comentarios(
            ids_videos, coletar_todos=self.configuracao.coletar_todos_comentarios
        )

        # 4. Coleta de respostas aos comentários principais
        respostas_novas: List[Resposta] = []
        if self.configuracao.coletar_respostas and comentarios_novos:
            respostas_novas = self.coletor_resposta.coletar_respostas(comentarios_novos)

        detalhes_conclusao = {
            "total_canais": str(len(canais_persistir)),
            "total_videos": str(len(ids_videos)),
            "total_comentarios": str(len(comentarios_novos)),
            "total_respostas": str(len(respostas_novas)),
        }
        self.publicador.publicar_evento("coleta_concluida", detalhes_conclusao)
        logger.info("Coleta diária finalizada com sucesso. %s", detalhes_conclusao)

        return comentarios_novos, respostas_novas
