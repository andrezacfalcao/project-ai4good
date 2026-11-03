# O que mudou do exemplo oficial para o Atlas do Erro

Compare o [primeiro commit](https://github.com/andrezacfalcao/project-ai4good/commit/ae9a9b4)
com o [segundo commit](https://github.com/andrezacfalcao/project-ai4good/commit/abf1638).
O [diff do código](resultados/adaptacao.diff) está salvo nesta pasta.

| Trecho novo | Por que existe |
| --- | --- |
| `sys.argv[1:]` e `Image.open(caminho)` | A entrada passa a ser cada imagem de uma resolução, fornecida pelo terminal. Sem argumento, o script mostra o uso. |
| `image.crop(...)` em três faixas | Cada imagem de teste contém três linhas igualmente espaçadas. O TrOCR recebe uma imagem por linha, como no exemplo original. Isso ainda não segmenta um caderno real de tamanho arbitrário. |
| `processor(images=faixas, ...)` e `batch_decode(...)` | Aplicam o mesmo processamento e OCR às três linhas. O checkpoint e a chamada `model.generate(pixel_values)` são os mesmos do exemplo oficial. |
| `raizes()` com `SymPy` | Interpreta cada igualdade e compara conjuntos-solução de linhas consecutivas para localizar a primeira mudança. Está limitado às equações simples desta demonstração. |
| `diagnostico` | Distingue quebra de equivalência de uma linha sem sinal `=`. Outros erros de sintaxe ainda podem interromper o script. |
| `PROMPT` e chamada HTTP ao Ollama | Pedem ao Qwen local uma categoria e uma pista em JSON, a partir do texto lido e da verificação simbólica. A chamada tem limite de 120 segundos. |
| `print(...)` | Mostra a transcrição, a primeira passagem incorreta e o texto devolvido pelo modelo, sem esconder os erros. |

Não há treinamento, alteração da arquitetura ou implementação de um novo OCR.
As bibliotecas SymPy e Qwen entram na etapa de saída, como técnicas de apoio.

## Limitações observadas na execução

- O primeiro caderno recebe uma categoria genérica e a linha já corrigida;
  o requisito pedagógico de oferecer apenas uma pista ainda não está garantido.
- No terceiro, o OCR confunde símbolos e o LLM inventa uma correção a partir
  da transcrição errada. A causa do erro visual não foi isolada em experimento.
- O modelo é voltado a texto impresso, não especializado em matemática manuscrita.
- As entradas são sintéticas; o código ainda não foi validado em fotos reais.
- `parse_expr` é usado somente neste experimento local com entradas controladas;
  não é um parser seguro para abrir o script como serviço com texto arbitrário.
- O código produz categorias por resolução, mas não agrega um atlas da turma.
