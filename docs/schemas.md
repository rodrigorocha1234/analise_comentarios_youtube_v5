# Schemas de Dados e Versionamento de Contratos

## 1. Contrato do Modelo (MLflow ModelSignature)

### Schema de Entrada (Versão 1.0.0)
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `texto` | string | Texto bruto do comentário ou resposta |
| `id_video` | string | Identificador do vídeo no YouTube |
| `id_canal` | string | Identificador do canal no YouTube |

### Schema de Saída (Versão 1.0.0)
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `numero_cluster` | long (int64) | Identificador numérico do cluster atribuído |
| `topico` | string | Exatamente UMA palavra representativa com acentuação correta |
| `probabilidade` | double (float64) | Grau de confiança ou densidade da atribuição |

## 2. Tabelas do Datalake MinIO (Parquet)

### Camada Bronze: Comentários e Respostas
- `id_comentario`: string
- `id_video`: string
- `id_canal`: string
- `id_comentario_pai`: string (vazio para comentários raiz)
- `tipo`: string ("COMENTARIO" ou "RESPOSTA")
- `texto`: string
- `autor`: string
- `data_publicacao`: string ISO-8601
- `data_atualizacao_youtube`: string ISO-8601
- `data_coleta`: string YYYY-MM-DD
- `hash_conteudo`: string SHA-256
- `versao`: int32
- `ativo`: bool

### Camada Gold: Trend Topics
- `escopo`: string ("video", "canal", "canal_video")
- `identificador_escopo`: string
- `janela_dias`: int32 (1, 3, 7, 14, 30)
- `data_coleta`: string YYYY-MM-DD
- `topico`: string (1 palavra)
- `numero_cluster`: int32
- `volume_atual`: int32
- `volume_anterior`: int32
- `crescimento_absoluto`: int32
- `crescimento_relativo`: float64
- `aceleracao`: float64
- `novidade`: float64
- `score_tendencia`: float64
- `posicao_ranking`: int32
