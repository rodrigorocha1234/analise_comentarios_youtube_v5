# Trend Topics Temporais Multiescopo

## Escopos Analíticos
O módulo `src/topicos/calculador_tendencia.py` calcula dinamicamente tendências em 3 níveis:
1. **Por Vídeo**: Identifica tópicos que se destacam dentro de um vídeo específico.
2. **Por Canal**: Identifica o direcionamento temático do canal como um todo.
3. **Por Canal × Vídeo**: Permite comparar o desempenho de tópicos entre diferentes vídeos do mesmo criador.

## Janelas Temporais
As métricas são avaliadas nas janelas móveis configuradas no YAML:
- 1 dia (ultrarrápido / comentários imediatos)
- 3 dias (curto prazo)
- 7 dias (semanal)
- 14 dias (quinzenal)
- 30 dias (mensal)

## Fórmula do Score de Tendência
Para evitar que apenas tópicos antigos e com alto volume absoluto dominem o ranking, o score composto valoriza a aceleração e o surgimento de novos temas:

$$\text{Score} = (0.40 \times \text{Crescimento Relativo}) + (0.25 \times \text{Aceleração}) + (0.20 \times \text{Novidade}) + (0.15 \times \ln(1 + \text{Volume Atual}))$$

Onde:
- **Crescimento Relativo**: $(\text{Vol}_{\text{atual}} - \text{Vol}_{\text{anterior}}) / \max(\text{Vol}_{\text{anterior}}, 1)$
- **Aceleração**: Variação absoluta dividida pelo número de dias da janela.
- **Novidade**: $1.0$ se o tópico for inédito no período anterior; caso contrário, a proporção do volume recente sobre o total acumulado.
- **Ranking**: Ordenação decrescente do score gerando `posicao_ranking` de cada tópico na janela.
