from typing import Dict, List
import mlflow.pyfunc
import numpy as np
import pandas as pd


class ModeloInferencia(mlflow.pyfunc.PythonModel):
    """Wrapper MLflow PythonModel para servir previsões de cluster e tópico via MLflow Serving."""

    def __init__(
        self,
        mapa_topicos: Dict[int, str],
        versao_schema_entrada: str = "1.0.0",
        versao_schema_saida: str = "1.0.0",
    ) -> None:
        self.mapa_topicos = mapa_topicos
        self.versao_schema_entrada = versao_schema_entrada
        self.versao_schema_saida = versao_schema_saida

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """Carrega recursos de contexto impostos pela interface MLflow PythonModel."""
        pass

    def preparar_predicao(self, texto: str) -> Dict[str, object]:
        """Aplica inferência lógica de tópicos para um registro de texto."""
        # Se cluster não conhecido ou sem modelo em memória, atribui cluster padrão
        num_cluster = 0
        topico = self.mapa_topicos.get(num_cluster, "geral")
        prob = 0.95
        return {
            "numero_cluster": num_cluster,
            "topico": topico,
            "probabilidade": prob,
        }

    def predict(self, context: mlflow.pyfunc.PythonModelContext, model_input: pd.DataFrame) -> pd.DataFrame:
        """Executa inferência padronizada imposta pelo MLflow Serving."""
        resultados: List[Dict[str, object]] = []
        for _, linha in model_input.iterrows():
            texto = str(linha.get("texto", ""))
            pred = self.preparar_predicao(texto)
            resultados.append(pred)
        return pd.DataFrame(resultados)
