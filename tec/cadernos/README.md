# Entradas de teste

Estas três imagens foram reaproveitadas da
[primeira demonstração, no commit `26f14db`](https://github.com/andrezacfalcao/project-ai4good/tree/26f14db/va2/tec/cadernos).
A pasta atual das entradas é `tec/cadernos/`. São **dados sintéticos de teste**, simulando resoluções em três
linhas; não são fotografias coletadas de estudantes nem uma avaliação escolar.
Não foi identificado um gerador dessas imagens no repositório.

| Arquivo | Transcrição esperada | Primeira passagem incorreta |
| --- | --- | --- |
| `caderno-1.png` | `2x + 4 = 10` → `2x = 10 + 4` → `x = 7` | linha 1 → linha 2 |
| `caderno-2.png` | `3x - 6 = 9` → `3x = 9 - 6` → `x = 1` | linha 1 → linha 2 |
| `caderno-3.png` | `4x + 8 = 20` → `4x = 20 + 8` → `x = 7` | linha 1 → linha 2 |

As duas primeiras imagens têm fundo limpo; a terceira inclui pauta azul e
escrita inclinada. Todas têm três linhas igualmente espaçadas, condição que
o recorte do script pressupõe. Uma foto real pode ter sombras, perspectiva,
linhas irregulares e símbolos diferentes. Ainda falta validar essa condição.

O script recebe apenas as imagens, não esta transcrição de referência.
