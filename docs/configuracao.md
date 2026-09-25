# Especificação de Configuração do Projeto

O comportamento do sistema é controlado pelo arquivo `config/configuracao.yaml`, permitindo ajustes operacionais sem alteração de código.

## Estrutura do YAML

```yaml
projeto:
  nome: agrupamento_youtube
  idioma: pt_BR

coleta:
  canais_alvo:
    - "UC_x5XG1OV2P6uZZ5FSM9Ttw" # IDs de canais monitorados
  videos_alvo: []                # IDs de vídeos pontuais opcionais
  intervalo_horas: 24
  coletar_respostas: true        # Habilita busca de comentários filhos
  coletar_todos_comentarios: true# Pagina todos os resultados disponíveis
  atualizar_comentarios: true    # Detecção incremental via hash
  maximo_videos_canal: 20

spacy:
  modelo: pt_core_news_md        # Modelo com vetores densos nativos (300 dimensões)
  lote: 256                      # Tamanho do lote para nlp.pipe

texto:
  lematizar: true
  remover_urls: true
  stopwords_adicionais:          # Stopwords unidas às nativas do spaCy
    - "valeu"
    - "vídeo"
    - "show"
    - "obrigado"

bertopic:
  top_n_words: 10

umap:
  n_neighbors: 15
  n_components: 5
  min_dist: 0.0
  metric: cosine
  random_state: 42

hdbscan:
  min_cluster_size: 15
  min_samples: 5
  metric: euclidean
  cluster_selection_method: eom
  prediction_data: true

execucao:
  modo: experimental             # 'experimental' (todos os 12 algoritmos) ou 'producao'
  modelos_producao:
    - bertopic
    - kmeans
    - hdbscan

tendencias:
  janelas_dias: [1, 3, 7, 14, 30]

armazenamento:
  bucket: youtube-comentarios
  formato: parquet

mlflow:
  experimento: agrupamento_youtube
  registrar_modelos: true
  versionar_schema: true
  versao_schema_entrada: "1.0.0"
  versao_schema_saida: "1.0.0"
```

## Regras de Segurança
- Nenhuma chave secreta ou credencial é gravada no YAML.
- Segredos (`YOUTUBE_API_KEY`, senhas do MinIO e URLs de serviço) residem exclusivamente no `.env`.
