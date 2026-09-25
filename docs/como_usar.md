# Guia Operacional — Como Usar o Projeto

Este guia permite que qualquer pessoa configure, execute e visualize os resultados do projeto **analise_comentarios_youtube** sem necessidade de conhecer os detalhes internos do código.

---

## 1. Pré-requisitos
- Sistema operacional Linux ou macOS (ou WSL2 no Windows).
- Docker e Docker Compose instalados.
- Python 3.10 ou superior (recomendado 3.11).
- Chave de API da YouTube Data API v3.

---

## 2. Configuração Inicial do Ambiente

### Passo 2.1 — Criar e Ativar Ambiente Virtual
No terminal, dentro da pasta raiz do projeto:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download pt_core_news_md
```

### Passo 2.2 — Configurar Variáveis de Ambiente
Copie o template e edite o arquivo `.env`:
```bash
cp .env.example .env
```
Preencha sua chave do YouTube no `.env`:
```dotenv
YOUTUBE_API_KEY=sua_chave_real_aqui
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
MINIO_BUCKET=youtube-comentarios
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
```

---

## 3. Inicializar a Infraestrutura (MinIO + MLflow + Postgres)

Suba os containers essenciais em segundo plano:
```bash
docker compose up -d postgres minio create-bucket mlflow
```

Acesse os serviços no navegador para conferir o status:
- **MinIO Console**: [http://localhost:9001](http://localhost:9001) (Usuário: `minio`, Senha: `minio123`)
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)

---

## 4. Configurar os Canais e Parâmetros

Abra o arquivo `config/configuracao.yaml` e defina os canais ou vídeos que deseja analisar:
```yaml
coleta:
  canais_alvo:
    - "UC_x5XG1OV2P6uZZ5FSM9Ttw" # Substitua pelo ID do canal do YouTube
  intervalo_horas: 24
  coletar_respostas: true
  coletar_todos_comentarios: true
  maximo_videos_canal: 20

execucao:
  modo: experimental # use 'experimental' para rodar os 12 algoritmos ou 'producao' para os principais
```

---

## 5. Executar o Pipeline Diário

Execute o script orquestrador:
```bash
python main.py
```

O pipeline executará automaticamente as seguintes fases:
1. **Bronze**: Conexão com YouTube Data API, descoberta de novos vídeos, coleta de comentários e respostas, detecção de alterações via hash e gravação no MinIO (`s3://youtube-comentarios/bronze/`).
2. **Silver**: Normalização textual spaCy, lematização, remoção de URLs, aplicação de stopwords e geração de embeddings densos de 300 dimensões (`s3://youtube-comentarios/silver/`).
3. **Gold**: Treinamento dos algoritmos de clustering (incluindo BERTopic), nomeação de tópicos com exatamente uma palavra, associação de documentos e cálculo de métricas (`s3://youtube-comentarios/gold/`).
4. **Tendências**: Cálculo de Trend Topics temporais nos 3 escopos (vídeo, canal, canal+vídeo) e nas janelas de 1, 3, 7, 14 e 30 dias.
5. **MLflow**: Publicação de métricas, parâmetros, contratos de schemas e registro de modelo no Model Registry.

---

## 6. Visualizar no Dashboard Streamlit

Inicie o painel interativo:
```bash
streamlit run src/painel/painel_streamlit.py
```
Acesse no navegador: [http://localhost:8501](http://localhost:8501).

O dashboard oferece 12 abas de exploração:
- **Visão Geral**: Estatísticas do ecossistema e tópicos mais populares.
- **Tendências**: Tabela dinâmica de Trend Topics temporais.
- **Vídeos**, **Canais** e **Canal × Vídeo**: Análise nos 3 escopos espaciais.
- **Tópicos** e **Clusters**: Exploração dos tópicos de uma palavra e seus agrupamentos.
- **Comentários**: Navegação hierárquica (comentário pai -> respostas encadeadas).
- **Nuvem de Palavras**: Frequências de palavras para canais, tópicos e geral.
- **Comparação de Modelos**: Seleção individual de qualquer um dos 12 algoritmos executados com métricas e distribuições comparativas.
- **Execuções MLflow**: Acesso rápido às runs rastreadas.
- **Qualidade**: Avaliação de Silhouette, Davies-Bouldin e ruído.

---

## 7. Execução dos Testes Automatizados

Para validar o funcionamento completo de ponta a ponta:
```bash
PYTHONPATH=. .venv/bin/pytest
```
Todos os 21 testes unitários e de integração serão executados, cobrindo:
- Descoberta e deduplicação de vídeos
- Versionamento incremental com hash de comentários e respostas
- Preservação estrita de acentos Unicode e português brasileiro
- Geração de embeddings densos spaCy
- Todas as 12 estratégias GoF e Factory
- BERTopic com embeddings spaCy
- Nomeação com exatamente uma palavra
- Padrão Observer no MLflow
- Contratos de schemas e predição no MLflow Serving
