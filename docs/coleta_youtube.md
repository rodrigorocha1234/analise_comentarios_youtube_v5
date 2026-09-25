# Coleta Incremental e Versionamento do YouTube

## Arquitetura de Coleta
O módulo `src/coleta/` é composto por 4 classes especializadas:
- `ColetorYoutube`: Executa chamadas HTTP autenticadas e tratadas à API v3.
- `ColetorVideo`: Responsável pela descoberta e deduplicação de vídeos.
- `ColetorComentario`: Pagina e versiona os comentários principais.
- `ColetorResposta`: Pagina e versiona as respostas atreladas a cada comentário pai.

## Lógica Incremental

### 1. Descoberta de Vídeos
- Ao consultar vídeos de um canal, o sistema recupera a lista de IDs conhecidos em `controle/videos_processados/videos_conhecidos.json`.
- **Vídeo Novo**: Persistido em `bronze/videos/data_coleta=YYYY-MM-DD/videos.parquet` e adicionado ao índice.
- **Vídeo Conhecido**: Não é duplicado na camada Bronze, mas permanece na lista de sincronização de comentários, pois pode receber novas interações.

### 2. Versionamento de Comentários e Respostas
Para cada comentário ou resposta:
1. Calcula-se o hash SHA-256 do texto: `hash_conteudo = sha256(texto.strip())`.
2. O sistema consulta o índice em `controle/comentarios_processados/indice_comentarios.json`.
3. **Novo Registro**:
   - Atribuído `versao = 1` e `ativo = True`.
   - Persistido no lote diário Bronze.
4. **Registro Já Existente**:
   - Se `hash_conteudo == hash_anterior`: nenhuma nova gravação ocorre.
   - Se `hash_conteudo != hash_anterior`: grava nova versão incrementada (`versao = versao_anterior + 1`), mantendo o histórico anterior preservado no datalake.
5. A mesma regra se aplica às respostas através de `ColetorResposta` e `indice_respostas.json`.
