# Visão Geral

## Objetivo
Plataforma sem LLM para coletar diariamente vídeos, comentários e respostas do YouTube, armazenar exclusivamente em MinIO/S3, gerar embeddings com spaCy, comparar técnicas de agrupamento não supervisionado, produzir tópicos e Trend Topics temporais e registrar/servir modelos via MLflow.

## Regras obrigatórias
- Sem LLM.
- Embeddings gerados pelo spaCy.
- BERTopic incluído, recebendo embeddings externos do spaCy.
- Datalake nunca local: somente MinIO/S3.
- Coleta uma vez ao dia.
- Coletar todos os comentários e todas as respostas disponíveis.
- Vídeo novo é persistido; vídeo conhecido não é duplicado.
- Comentário/resposta novo é persistido; existente só ganha nova versão quando alterado.
- Nome exibido do tópico contém exatamente uma palavra e preserva Unicode/acentos/cedilha.
- Cada resultado contém número do cluster e palavra representativa.
- Dashboard permite chegar do tópico/cluster aos comentários e respostas relacionados.
- Uma classe por arquivo .py.
- Pacotes, módulos, classes, atributos e métodos próprios em português.
- Métodos próprios: duas palavras separadas por underscore.
- Proibido Any no código da aplicação.
- Preferir operações vetorizadas, nlp.pipe, pandas/numpy e itertools a loops desnecessários.
- Configuração funcional em YAML; segredos no .env.
- Logs por etapa.
