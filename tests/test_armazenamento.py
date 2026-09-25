from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from botocore.exceptions import EndpointConnectionError

from src.armazenamento.adaptador_s3 import AdaptadorS3


def test_falha_conexao_minio_sem_fallback_local():
    with patch("boto3.client") as mock_boto:
        mock_cliente = MagicMock()
        mock_cliente.head_bucket.side_effect = EndpointConnectionError(endpoint_url="http://minio:9000")
        mock_boto.return_value = mock_cliente

        with pytest.raises(ConnectionError) as exc_info:
            AdaptadorS3(endpoint_url="http://minio:9000", bucket="teste-bucket")

        assert "MinIO indisponível" in str(exc_info.value)


def test_gravacao_e_leitura_dataframe_s3():
    with patch("boto3.client") as mock_boto:
        mock_cliente = MagicMock()
        mock_cliente.head_bucket.return_value = {}
        mock_boto.return_value = mock_cliente

        adaptador = AdaptadorS3(bucket="teste-bucket")

        df_orig = pd.DataFrame([{"col1": "a", "col2": 1}, {"col1": "b", "col2": 2}])
        sucesso = adaptador.gravar_dataframe("dados.parquet", df_orig)
        assert sucesso is True
        assert mock_cliente.put_object.called

        # Mock leitura de objeto
        import io
        buf = io.BytesIO()
        df_orig.to_parquet(buf, index=False, engine="pyarrow")
        mock_cliente.get_object.return_value = {"Body": io.BytesIO(buf.getvalue())}

        df_lido = adaptador.ler_dataframe("dados.parquet")
        assert len(df_lido) == 2
        assert list(df_lido["col1"]) == ["a", "b"]
