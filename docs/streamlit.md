# Dashboard Interativo Streamlit

## Visão Geral
O painel analítico é implementado na classe `PainelStreamlit` (`src/painel/painel_streamlit.py`), oferecendo visualização direta a partir dos dados do MinIO S3 (camada Gold).

## Inicialização Local
```bash
streamlit run src/painel/painel_streamlit.py --server.port 8501
```

## Abas do Painel

1. **Visão Geral**: Métricas consolidadas (documentos, tópicos, vídeos, canais) e gráfico dos tópicos mais frequentes.
2. **Tendências**: Tabela dinâmica dos Trend Topics temporais por janela (1, 3, 7, 14, 30 dias).
3. **Vídeos**: Tendências filtradas por vídeo individual.
4. **Canais**: Tendências agregadas no nível de canal.
5. **Canal × Vídeo**: Cruzamento e comparação temporal de tópicos entre vídeos do mesmo criador.
6. **Tópicos**: Detalhamento dos tópicos descobertos e contagem de documentos associados.
7. **Clusters**: Associação direta entre id do documento, cluster numérico, probabilidade e modelo.
8. **Comentários**: Navegação hierárquica preservando a relação entre comentário pai e suas respectivas respostas.
9. **Nuvem de Palavras**: Frequências lexicais em múltiplas granularidades (global, tópicos, canais).
10. **Comparação de Modelos** (Obrigatória): Seletor de todos os 12 algoritmos executados com métricas e distribuições comparativas.
11. **Execuções MLflow**: Link e status das execuções rastreadas no servidor MLflow.
12. **Qualidade**: Tabela comparativa de métricas geométricas (Silhouette, Davies-Bouldin, ruído).
