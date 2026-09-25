# Guia de Instalação e Configuração de Ambiente

## Pré-requisitos
- Python 3.10 ou superior (recomendado 3.11)
- Docker e Docker Compose instalados
- Chave de acesso da YouTube Data API v3

## Passo a Passo

### 1. Clonar o Repositório e Criar Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Download do Modelo spaCy PT-BR
Para suportar geração de embeddings densos de 300 dimensões:
```bash
python -m spacy download pt_core_news_md
```

### 3. Configurar Variáveis de Ambiente
Crie o arquivo `.env` baseado no `.env.example`:
```bash
cp .env.example .env
```
Edite o `.env` informando a sua `YOUTUBE_API_KEY`:
```dotenv
YOUTUBE_API_KEY=AIzaSy...
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
MINIO_BUCKET=youtube-comentarios
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
```

### 4. Inicializar Infraestrutura Docker
```bash
docker compose up -d postgres minio create-bucket mlflow
```
Verifique se os serviços estão saudáveis:
- MinIO Console: `http://localhost:9001`
- MLflow Tracking: `http://localhost:5000`
