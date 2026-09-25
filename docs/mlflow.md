# Integração e Governança com MLflow

## Padrão Observer no MLflow
A integração com o MLflow é totalmente desacoplada através do padrão GoF Observer (`ObservadorMlflow`).
O pipeline emite eventos padronizados (`EventoPipeline`), e o observador traduz esses eventos nas operações correspondentes:

- `coleta_iniciada` / `coleta_concluida`: Inicia run e registra métricas de volume de canais, vídeos e comentários.
- `processamento_concluido`: Registra quantidade de documentos normalizados no Silver.
- `embeddings_gerados`: Loga parâmetros de dimensão e modelo do spaCy.
- `treinamento_iniciado` / `avaliacao_concluida`: Cria runs filhas por algoritmo registrando hiperparâmetros, Silhouette Score, Davies-Bouldin e percentual de ruído.
- `modelo_registrado`: Publica o modelo aprovado no Model Registry com tags de versão de contrato.
- `execucao_concluida`: Finaliza a run principal.

## Configuração do Backend e Artefatos
- **Backend Store**: PostgreSQL (`postgresql+psycopg2://...`).
- **Artifacts Store**: MinIO S3 (`s3://youtube-comentarios/` ou `s3://mlflow/`).
- Não há gravação de artefatos de modelo em pastas locais da aplicação.
