# API e MLflow Serving

## Arquitetura de Inferência
O serving de inferência do projeto é implementado através do **MLflow Models Serving**.
A classe `ModeloInferencia` (`src/servicos/modelo_inferencia.py`) herda de `mlflow.pyfunc.PythonModel` e expõe a rota padrão de predição.

## Inicialização do Serving
O container `mlflow-serving` (ou comando `mlflow models serve`) disponibiliza o endpoint HTTP na porta `5002` (ou porta configurada):

```bash
mlflow models serve \
  -m "models:/agrupamento_youtube_bertopic@champion" \
  -p 5002 \
  --host 0.0.0.0 \
  --no-conda
```

## Exemplo de Requisição (Entrada)
Formato JSON compatível com o schema versionado `1.0.0`:

```json
{
  "dataframe_records": [
    {
      "texto": "Essa produção musical ficou de altíssimo nível, parabéns!",
      "id_video": "vid_exemplo_123",
      "id_canal": "can_exemplo_456"
    }
  ]
}
```

## Exemplo de Resposta (Saída)
Retorno estrito conforme o contrato registrado:

```json
[
  {
    "numero_cluster": 1,
    "topico": "produção",
    "probabilidade": 0.95
  }
]
```
