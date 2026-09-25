from abc import ABC, abstractmethod
from typing import List
import pandas as pd


class ArmazenamentoObjeto(ABC):
    """Interface abstrata do adaptador de armazenamento de objetos em nuvem/MinIO."""

    @abstractmethod
    def gravar_objeto(self, caminho: str, conteudo: bytes) -> bool:
        """Grava bytes no caminho especificado do bucket."""
        pass

    @abstractmethod
    def ler_objeto(self, caminho: str) -> bytes:
        """Lê os bytes de um objeto do bucket."""
        pass

    @abstractmethod
    def listar_objetos(self, prefixo: str) -> List[str]:
        """Lista os caminhos dos objetos com o prefixo informado."""
        pass

    @abstractmethod
    def objeto_existe(self, caminho: str) -> bool:
        """Verifica se determinado objeto existe no bucket."""
        pass

    @abstractmethod
    def gravar_dataframe(self, caminho: str, dados: pd.DataFrame) -> bool:
        """Grava um DataFrame pandas no formato parquet diretamente no bucket."""
        pass

    @abstractmethod
    def ler_dataframe(self, caminho: str) -> pd.DataFrame:
        """Lê um arquivo parquet do bucket e retorna como DataFrame pandas."""
        pass
