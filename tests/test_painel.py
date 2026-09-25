from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from src.painel.painel_streamlit import PainelStreamlit


def test_inicializacao_painel_e_carregamento_vazio():
    with patch("boto3.client") as mock_boto:
        mock_cliente = MagicMock()
        mock_cliente.head_bucket.return_value = {}
        mock_boto.return_value = mock_cliente

        painel = PainelStreamlit()
        df = painel.carregar_dados("gold/inexistente/")
        assert isinstance(df, pd.DataFrame)
        assert df.empty
