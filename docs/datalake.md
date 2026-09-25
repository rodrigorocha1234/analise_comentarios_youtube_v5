# Datalake MinIO / S3

## Regra de Ouro da Camada de Dados
> **HARD LOCK 4 & 5:** O datalake NUNCA pode ser persistido localmente em disco. Todo dado Bronze, Silver e Gold deve ser persistido exclusivamente em MinIO/S3 utilizando protocolo S3 padrão. Não há fallback silencioso para disco local.

## Estrutura de Particionamento
Todos os arquivos são gravados no formato colunar **Apache Parquet**:

```text
s3://youtube-comentarios/
  bronze/
    canais/data_coleta=YYYY-MM-DD/canais.parquet
    videos/data_coleta=YYYY-MM-DD/videos.parquet
    comentarios/data_coleta=YYYY-MM-DD/comentarios.parquet
    respostas/data_coleta=YYYY-MM-DD/respostas.parquet
  silver/
    comentarios/data=YYYY-MM-DD/
    respostas/data=YYYY-MM-DD/
    documentos/data=YYYY-MM-DD/documentos.parquet
    embeddings/data=YYYY-MM-DD/embeddings.parquet
  gold/
    agrupamentos/modelo=<nome>/agrupamentos.parquet
    topicos/modelo=<nome>_topicos.parquet
    comentarios_topicos/
    tendencias_video/data_coleta=YYYY-MM-DD/tendencias.parquet
    tendencias_canal/data_coleta=YYYY-MM-DD/tendencias.parquet
    tendencias_canal_video/data_coleta=YYYY-MM-DD/tendencias.parquet
    nuvens_palavras/data_coleta=YYYY-MM-DD/frequencias.json
    metricas/modelo=<nome>_metricas.parquet
  controle/
    videos_processados/videos_conhecidos.json
    comentarios_processados/indice_comentarios.json
    respostas_processadas/indice_respostas.json
    execucoes/
```

## Adaptador de Armazenamento
O domínio interage unicamente com a interface abstrata `ArmazenamentoObjeto`. A classe `AdaptadorS3` gerencia streams em memória (`io.BytesIO`) conectados ao cliente `boto3`. Caso o MinIO esteja inacessível, uma exceção explícita é lançada e logada, abortando o pipeline com integridade.
