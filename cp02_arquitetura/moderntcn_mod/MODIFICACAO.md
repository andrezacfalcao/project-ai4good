# Modificação: atenção sobre patches com ganho inicial zero (ReZero)

**Base:** ModernTCN (Luo e Wang, ICLR 2024), código oficial em [`../moderntcn_oficial`](../moderntcn_oficial).

**Hipótese.** Os kernels grandes do ModernTCN (51) são pesos fixos: filtram toda entrada do
mesmo jeito. Uma camada de auto-atenção sobre os patches deixa o modelo ponderar o passado
conforme a entrada, o que pode ajudar em séries não estacionárias como a ETTh2. Esperamos
um MSE menor que o do baseline oficial, mas o custo é maior capacidade (+22 mil parâmetros) numa base pequena
(8.209 janelas de treino), então o resultado pode ser nulo ou negativo.

**O que muda** (`models/ModernTCN.py`, classe `PatchAttention`, ativada por `--use_attn 1`):

```
x -> [bloco ModernTCN: DWConv 51 + ConvFFN1 + ConvFFN2] -> + residual
  -> x + gamma * MultiHeadAttention(LayerNorm(x) + posição)     # novo
```

- tokens = os 84 patches de cada variável, embedding de 64, 4 cabeças, dropout do bloco;
- posição aprendida, porque a atenção ignora a ordem;
- `gamma` é um escalar aprendido que **começa em 0**: no início o modelo é idêntico ao oficial
  (`../testar_modificacao.py` confere isso), e qualquer diferença nos resultados é aprendida;
- hiperparâmetros de treino idênticos aos do baseline; só a flag muda.

**Custo:** 681.989 parâmetros contra 659.844 (+3,4%).

**Onde está no código:** `models/ModernTCN.py` (classe `PatchAttention` e as linhas marcadas com
`[MODIFICAÇÃO CP02]`) e a flag em `run.py`. [`DIFF_vs_oficial.patch`](DIFF_vs_oficial.patch) lista
exatamente o que difere do oficial: 53 linhas acrescentadas e 8 alteradas.
