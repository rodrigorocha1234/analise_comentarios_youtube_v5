# Coleta YouTube

## Frequência
Uma execução diária. A chave é lida de `YOUTUBE_API_KEY` no `.env`.

## Vídeos
Consultar IDs descobertos contra o controle. ID novo: persistir metadados e iniciar coleta. ID conhecido: não duplicar o vídeo, mas continuar sincronizando seus comentários conforme a política configurada.

## Comentários e respostas
Paginar até coletar todos os comentários disponíveis. Para cada thread, coletar comentário principal e todas as respostas. Não assumir que respostas embutidas no thread sejam completas; quando necessário, paginar respostas pelo comentário pai.

## Atualizações
Calcular hash do conteúdo relevante. Novo ID -> versão 1. ID existente e hash igual -> nenhuma gravação. ID existente e hash diferente -> gravar nova versão, preservando histórico. A mesma regra vale para respostas.
