# Raio-X do dataset `songdj/ScratchMath` (`middle` — 7º ao 9º ano)

- **Total de amostras:** 241
- **Baseline majoritário (chutar sempre `erro_calculo`):** 113/241 (46.9%)
- **Resolução das fotos:** largura 1920–2880 px (mediana 2160), altura 1056–5824 px (mediana 1288)

## Distribuição das 7 categorias (GT dos professores)

| ID | Código | Chinês | Português | Qtd | % |
|---:|:---|:---|:---|---:|---:|
| 0 | `erro_calculo` | 计算错误 | Erro de cálculo | 113 | 46.9% |
| 1 | `erro_compreensao` | 题目理解错误 | Erro de compreensão do enunciado | 20 | 8.3% |
| 2 | `lacuna_conhecimento` | 知识点错误 | Lacuna de conhecimento ou conceito | 45 | 18.7% |
| 3 | `erro_estrategia` | 答题技巧错误 | Erro de estratégia ou método | 17 | 7.1% |
| 4 | `erro_transcricao` | 手写誊抄错误 | Erro de transcrição ou cópia manuscrita | 29 | 12.0% |
| 5 | `erro_raciocinio` | 逻辑推理错误 | Erro de raciocínio lógico | 2 | 0.8% |
| 6 | `erro_atencao` | 注意力与细节错误 | Erro de atenção e detalhes | 15 | 6.2% |

## Distribuição heurística de tipos de questão

| Tipo heurístico | Qtd | % |
|:---|---:|---:|
| `expressao_ou_equacao_com_variavel` | 119 | 49.4% |
| `problema_textual_ou_outro` | 56 | 23.2% |
| `equacao_explicita` | 44 | 18.3% |
| `geometria` | 12 | 5.0% |
| `calculo_ou_simplificacao` | 10 | 4.1% |

## Um exemplo real por categoria

### 0 · `erro_calculo` (Erro de cálculo / 计算错误)
- **Idx / ID:** `000` / `a0916973ce57681ca8bddd2cae12d15d` (2000×1056)
- **Questão:** 计算：$4x - 3(20 - x) = 6x - 7(9 - x)$的解是x=____
- **Resposta certa:** `\frac{1}{2}, 0.5` | **Resposta aluno:** `-\frac{1}{2}`
- **Explicação GT:** 学生在最后一步中，错误地将 \(-6x = -3\) 解为 \(x = -\frac{1}{2}\)，而不是正确的 \(x = \frac{1}{2}\)，导致错误答案。

### 1 · `erro_compreensao` (Erro de compreensão do enunciado / 题目理解错误)
- **Idx / ID:** `014` / `f8b534a06dc69beba2c9ff4587dac51c` (2000×2162)
- **Questão:** 若关于x的一元二次方程（k﹣1）${x^2}$+4x+1=0有实数根，则k的取值范围是____．
- **Resposta certa:** `k\leq 5且k\neq 1, k\neq 1且k\leq 5` | **Resposta aluno:** `k\le5`
- **Explicação GT:** 学生在解题过程中忽略了题目中关于\(k \neq 1\)的条件，导致最终答案不完整。

### 2 · `lacuna_conhecimento` (Lacuna de conhecimento ou conceito / 知识点错误)
- **Idx / ID:** `005` / `34076d19bdb911e999b77cd30a5a3038` (2160×1288)
- **Questão:** 解方程：$80\% x -30\% x = 200$,那么该方程的解x=____
- **Resposta certa:** `400` | **Resposta aluno:** `4`
- **Explicação GT:** 学生错误地将百分数视为整数，未正确使用百分数符号，导致方程设置错误。

### 3 · `erro_estrategia` (Erro de estratégia ou método / 答题技巧错误)
- **Idx / ID:** `017` / `deb2db0d3cd2191edbc3751dc74d4cde` (2000×1074)
- **Questão:** 关于x的方程$a{(x + m)^2} + b = 0$的解是${x_1}= 2$，${x_2} =- 1$，(a，b，m均为常数，a≠0)，则方程$a{(x + m + 2)^2} + b = 0$的解是 $x$=____．
- **Resposta certa:** `0或-3, -3或0, $0, -3$, $-3, 0$` | **Resposta aluno:** `-3和0`
- **Explicação GT:** 学生在填写答案时未按要求使用“或”连接两个答案，导致答案格式错误。

### 4 · `erro_transcricao` (Erro de transcrição ou cópia manuscrita / 手写誊抄错误)
- **Idx / ID:** `001` / `3401b94ebdb911e999b77cd30a5a3038` (2160×1288)
- **Questão:** 解方程：$\frac{{0.02 - 0.1x}}{{0.03}} - 1 =\frac{{1 - 3x}}{{2.5}}$,那么该方程的解x=____
- **Resposta certa:** `-\frac{{11}}{{32}}, - 0.34375` | **Resposta aluno:** `\frac{1}{32}`
- **Explicação GT:** 学生在步骤4中错误地将3-5视为3.5，导致后续计算错误，并且最终填写的答案与草稿中算出的有出入，可能存在抄写错误。

### 5 · `erro_raciocinio` (Erro de raciocínio lógico / 逻辑推理错误)
- **Idx / ID:** `127` / `4e2a7a1bf54011e999b77cd30a5a3038` (2160×1288)
- **Questão:** 某校志愿者团队在重阳节购买了一批牛奶到“夕阳红”敬老院慰问孤寡老人，如果给每个老人分5盒，则剩下38盒，如果给每个老人分6盒，则最后一个老人不足5盒，但至少分得一盒．则该敬老院至少有____名老人，最多有____名老人
- **Resposta certa:** `40, 43` | **Resposta aluno:** `39","40`
- **Explicação GT:** 学生在建立不等式时误解了题意，未能正确考虑每个老人分6盒的情况，导致不等式错误，最终答案不正确。

### 6 · `erro_atencao` (Erro de atenção e detalhes / 注意力与细节错误)
- **Idx / ID:** `002` / `3400ac28bdb911e999b77cd30a5a3038` (2160×1288)
- **Questão:** 解方程：$\frac{{2x}}{{0.03}}+ \frac{{65}}{{0.3}} - \frac{{14 - 3x}}{{0.02}} = 0$,那么该方程的解x=____
- **Resposta certa:** `\frac{{29}}{{13}}, 2\frac{3}{{13}}` | **Resposta aluno:** `-8.14`
- **Explicação GT:** 学生在去分母时忽略了负号，将 \(-900x\) 错误地写成了 \(+900x\)，导致方程整理错误，最终结果错误。
