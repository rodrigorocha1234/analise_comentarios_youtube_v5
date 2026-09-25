# Datalake MinIO/S3

Bucket sugerido: `youtube-comentarios`. Nenhuma camada persistente pode usar disco local.

```text
s3://youtube-comentarios/
  bronze/canais/data_coleta=YYYY-MM-DD/
  bronze/videos/data_coleta=YYYY-MM-DD/
  bronze/comentarios/data_coleta=YYYY-MM-DD/
  bronze/respostas/data_coleta=YYYY-MM-DD/
  silver/comentarios/data=YYYY-MM-DD/
  silver/respostas/data=YYYY-MM-DD/
  silver/documentos/data=YYYY-MM-DD/
  silver/embeddings/data=YYYY-MM-DD/
  gold/agrupamentos/modelo=<nome>/
  gold/topicos/
  gold/comentarios_topicos/
  gold/tendencias_video/
  gold/tendencias_canal/
  gold/tendencias_canal_video/
  gold/nuvens_palavras/
  gold/metricas/
  controle/videos_processados/
  controle/comentarios_processados/
  controle/respostas_processadas/
  controle/execucoes/
```

Formato preferencial: Parquet. Bronze preserva origem; Silver normaliza/processa; Gold serve análise/dashboard/API.
