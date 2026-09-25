# Observabilidade, Logs e Governança

## Padrão Estruturado de Logs
As mensagens de log do sistema são padronizadas e emitem contexto operacional claro a cada etapa do processamento:

```text
YYYY-MM-DD HH:MM:SS | INFO    | Iniciando coleta diária do YouTube para a data 2026-09-24.
YYYY-MM-DD HH:MM:SS | INFO    | Consultando vídeos para o canal: UC_x5XG1OV2P6uZZ5FSM9Ttw
YYYY-MM-DD HH:MM:SS | INFO    | Persistindo 5 novos vídeos na camada Bronze.
YYYY-MM-DD HH:MM:SS | INFO    | Coletando comentários do vídeo: abc123xyz
YYYY-MM-DD HH:MM:SS | INFO    | Persistindo 85 novos/atualizados comentários na camada Bronze.
YYYY-MM-DD HH:MM:SS | INFO    | Iniciando processamento textual spaCy para 85 itens.
YYYY-MM-DD HH:MM:SS | INFO    | Gerando embeddings spaCy (pt_core_news_md) em lote...
YYYY-MM-DD HH:MM:SS | INFO    | Modelo spaCy pt_core_news_md validado com dimensões: 300
YYYY-MM-DD HH:MM:SS | INFO    | Executando agrupamento com algoritmo: BERTopic
YYYY-MM-DD HH:MM:SS | INFO    | Executando agrupamento com algoritmo: KMeans
YYYY-MM-DD HH:MM:SS | INFO    | Calculando Trend Topics temporais para a data 2026-09-24.
YYYY-MM-DD HH:MM:SS | INFO    | Registrando modelo bertopic no MLflow Model Registry...
YYYY-MM-DD HH:MM:SS | INFO    | Pipeline executado com sucesso de ponta a ponta.
```

## Diretrizes de Segurança
- Proibido logar chaves de API, senhas, tokens ou dados sensíveis.
- Erros de conexão ou autenticação são mascarados antes da gravação do log.
- O histórico de execuções é persistido no MinIO em `controle/execucoes/` e nas runs do MLflow.
