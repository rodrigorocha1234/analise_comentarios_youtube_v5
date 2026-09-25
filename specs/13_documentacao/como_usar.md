# Como usar

## Dependências principais
```bash
pip install -U bertopic sentence-transformers umap-learn hdbscan
pip install spacy
python -m spacy download pt_core_news_sm
```
`sentence-transformers` pode permanecer como dependência transitiva/ecossistema do BERTopic, mas não é a fonte de embeddings deste projeto. Para embeddings spaCy, instalar/configurar um pipeline PT-BR com vetores adequados e validá-lo.

## Fluxo
1. Subir a infraestrutura Docker Compose com MinIO e MLflow.
2. Criar `.env` com YouTube, MinIO e MLflow.
3. Ajustar `configuracao.yaml`.
4. Validar bucket MinIO.
5. Executar coleta diária.
6. Conferir Bronze.
7. Normalizar Silver.
8. Processar textos/stopwords no spaCy.
9. Gerar embeddings spaCy.
10. Executar estratégias de agrupamento.
11. Nomear tópicos e associar documentos.
12. Calcular tendências por vídeo, canal e canal+vídeo.
13. Persistir Gold.
14. Registrar runs, schemas e modelos no MLflow.
15. Promover modelo aprovado.
16. Iniciar MLflow Serving.
17. Iniciar Streamlit e validar resultados por modelo.
