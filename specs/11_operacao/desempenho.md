# Desempenho

Preferir `nlp.pipe`, NumPy, operações vetorizadas do pandas, `groupby`, `merge`, `explode`, `transform`, `map`, `zip` e `itertools`. Loops explícitos são permitidos quando tornam a lógica mais clara ou são necessários para paginação/IO.

Para grande volume, MiniBatchKMeans/BIRCH/HDBSCAN podem ser mais operacionais que técnicas com custo quadrático. Separar modo experimental de produção.
