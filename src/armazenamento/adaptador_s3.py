import io
import logging
import os
from typing import List, Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
import pandas as pd

from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto

logger = logging.getLogger(__name__)


class AdaptadorS3(ArmazenamentoObjeto):
    """Adaptador concreto para armazenamento de objetos MinIO/S3."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None,
        region_name: str = "us-east-1",
    ) -> None:
        self.endpoint_url: str = endpoint_url or os.getenv("MINIO_ENDPOINT") or f"http://{os.getenv('MINIO_HOST', 'localhost')}:{os.getenv('MINIO_PORT', '9000')}"
        self.access_key: str = access_key or os.getenv("MINIO_ACCESS_KEY") or os.getenv("MINIO_ROOT_USER", "minio")
        self.secret_key: str = secret_key or os.getenv("MINIO_SECRET_KEY") or os.getenv("MINIO_ROOT_PASSWORD", "minio123")
        self.bucket: str = bucket or os.getenv("MINIO_BUCKET", "youtube-comentarios")
        self.region_name: str = region_name

        self._cliente_s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
            config=Config(signature_version="s3v4"),
        )
        self.garantir_bucket()

    def garantir_bucket(self) -> bool:
        """Garante que o bucket configurado existe no MinIO/S3."""
        try:
            self._cliente_s3.head_bucket(Bucket=self.bucket)
            return True
        except ClientError:
            try:
                self._cliente_s3.create_bucket(Bucket=self.bucket)
                logger.info("Bucket %s criado com sucesso no MinIO/S3.", self.bucket)
                return True
            except Exception as erro:
                logger.error("Falha ao criar bucket %s: %s", self.bucket, erro)
                raise RuntimeError(f"Falha de infraestrutura MinIO/S3: {erro}") from erro
        except EndpointConnectionError as erro:
            logger.error("Servidor MinIO inacessível em %s: %s", self.endpoint_url, erro)
            raise ConnectionError(f"MinIO indisponível no endpoint {self.endpoint_url}") from erro

    def gravar_objeto(self, caminho: str, conteudo: bytes) -> bool:
        """Grava bytes no caminho especificado do bucket MinIO/S3."""
        try:
            self._cliente_s3.put_object(
                Bucket=self.bucket,
                Key=caminho,
                Body=conteudo,
            )
            return True
        except Exception as erro:
            logger.error("Erro ao gravar objeto %s no MinIO: %s", caminho, erro)
            raise RuntimeError(f"Erro ao persistir no MinIO: {erro}") from erro

    def ler_objeto(self, caminho: str) -> bytes:
        """Lê os bytes de um objeto do bucket MinIO/S3."""
        try:
            resposta = self._cliente_s3.get_object(
                Bucket=self.bucket,
                Key=caminho,
            )
            return resposta["Body"].read()
        except Exception as erro:
            logger.error("Erro ao ler objeto %s do MinIO: %s", caminho, erro)
            raise FileNotFoundError(f"Objeto {caminho} não encontrado no MinIO: {erro}") from erro

    def listar_objetos(self, prefixo: str) -> List[str]:
        """Lista as chaves de objetos com o prefixo informado."""
        try:
            paginador = self._cliente_s3.get_paginator("list_objects_v2")
            resultados: List[str] = []
            for pagina in paginador.paginate(Bucket=self.bucket, Prefix=prefixo):
                if "Contents" in pagina:
                    for obj in pagina["Contents"]:
                        resultados.append(str(obj["Key"]))
            return resultados
        except Exception as erro:
            logger.error("Erro ao listar objetos com prefixo %s: %s", prefixo, erro)
            raise RuntimeError(f"Erro ao listar objetos no MinIO: {erro}") from erro

    def objeto_existe(self, caminho: str) -> bool:
        """Verifica se determinado objeto existe no bucket."""
        try:
            self._cliente_s3.head_object(Bucket=self.bucket, Key=caminho)
            return True
        except ClientError:
            return False
        except Exception as erro:
            logger.error("Erro ao consultar existência de %s: %s", caminho, erro)
            return False

    def gravar_dataframe(self, caminho: str, dados: pd.DataFrame) -> bool:
        """Grava DataFrame em formato Parquet no MinIO sem persistência em disco local."""
        try:
            buffer = io.BytesIO()
            dados.to_parquet(buffer, index=False, engine="pyarrow")
            buffer.seek(0)
            self._cliente_s3.put_object(
                Bucket=self.bucket,
                Key=caminho,
                Body=buffer.getvalue(),
            )
            return True
        except Exception as erro:
            logger.error("Erro ao gravar DataFrame Parquet em %s: %s", caminho, erro)
            raise RuntimeError(f"Erro ao persistir Parquet no MinIO: {erro}") from erro

    def ler_dataframe(self, caminho: str) -> pd.DataFrame:
        """Lê Parquet diretamente do MinIO em memória para DataFrame pandas."""
        try:
            conteudo = self.ler_objeto(caminho)
            buffer = io.BytesIO(conteudo)
            return pd.read_parquet(buffer, engine="pyarrow")
        except Exception as erro:
            logger.error("Erro ao ler DataFrame Parquet de %s: %s", caminho, erro)
            raise RuntimeError(f"Erro ao ler Parquet do MinIO: {erro}") from erro
