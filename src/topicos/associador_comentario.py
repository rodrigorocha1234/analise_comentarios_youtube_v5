import collections
import logging
from typing import Dict, List, Tuple
import numpy as np

from src.dominio.agrupamento import Agrupamento
from src.dominio.documento_processado import DocumentoProcessado
from src.dominio.topico import Topico

logger = logging.getLogger(__name__)


class AssociadorComentario:
    """Associa documentos processados a clusters/tópicos e estrutura a relação comentário-resposta."""

    def __init__(self) -> None:
        pass

    def associar_documentos(
        self,
        documentos: List[DocumentoProcessado],
        rotulos: np.ndarray,
        probabilidades: np.ndarray,
        mapa_topicos: Dict[int, Topico],
        nome_modelo: str,
        versao_modelo: str = "1.0.0",
    ) -> List[Agrupamento]:
        """Cria registros de Agrupamento relacionando documento, cluster e nome do tópico."""
        agrupamentos: List[Agrupamento] = []
        total = min(len(documentos), len(rotulos))

        for i in range(total):
            doc = documentos[i]
            cluster_id = int(rotulos[i])
            prob = float(probabilidades[i]) if i < len(probabilidades) else 1.0
            topico_obj = mapa_topicos.get(cluster_id)
            nome_topico = topico_obj.palavra_representativa if topico_obj else f"Cluster_{cluster_id}"

            item = Agrupamento(
                id_documento=doc.id_documento,
                id_video=doc.id_video,
                id_canal=doc.id_canal,
                id_comentario=doc.id_comentario,
                id_comentario_pai=doc.id_comentario_pai,
                tipo=doc.tipo,
                numero_cluster=cluster_id,
                topico=nome_topico,
                probabilidade=prob,
                data_publicacao=doc.data_publicacao,
                texto_original=doc.texto_original,
                modelo=nome_modelo,
                versao_modelo=versao_modelo,
            )
            agrupamentos.append(item)

        return agrupamentos

    def agrupar_hierarquia(
        self, agrupamentos: List[Agrupamento]
    ) -> Dict[str, Tuple[Agrupamento, List[Agrupamento]]]:
        """Agrupa comentários pais e suas respectivas respostas em estruturas hierárquicas."""
        pais: Dict[str, Agrupamento] = {}
        respostas_por_pai: Dict[str, List[Agrupamento]] = collections.defaultdict(list)

        for agr in agrupamentos:
            if agr.tipo == "COMENTARIO":
                pais[agr.id_comentario] = agr
            elif agr.tipo == "RESPOSTA":
                respostas_por_pai[agr.id_comentario_pai].append(agr)

        hierarquia: Dict[str, Tuple[Agrupamento, List[Agrupamento]]] = {}
        for id_com, pai in pais.items():
            hierarquia[id_com] = (pai, respostas_por_pai.get(id_com, []))

        return hierarquia

    def obter_respostas(
        self, id_comentario_pai: str, hierarquia: Dict[str, Tuple[Agrupamento, List[Agrupamento]]]
    ) -> List[Agrupamento]:
        """Recupera lista de respostas associadas a um comentário pai."""
        if id_comentario_pai in hierarquia:
            return hierarquia[id_comentario_pai][1]
        return []
