# Relatório de Execução Técnica e Controles de Repetição

- **Rodadas concluídas:** 20 de 20 (100% de conclusão).
- **Etapas locais executadas:** 40 etapas (2 turnos por rodada).
- **Total de requisições ao modelo local (com retentativas):** 64.
- **Etapas que exigiram retentativa:** 16.
- **Tentativas rejeitadas pelos filtros heurísticos:** 29.
- **Etapas sem aprovação em todos os filtros após 3 tentativas:** 5.

## Arquitetura e Modelos
- **Agente 1 (Trabalhista):** Antigravity (Gemini) — opera remotamente gerando propostas regulatórias e defesas pragmáticas.
- **Agente 2 (Liberal):** Qwen 2.5 1.5B — opera localmente via servidor Ollama na máquina do usuário.
- **Agente 3 (Juiz):** Antigravity (Gemini) — síntese imparcial, emissão de vereditos e preservação da memória de debate.

## Mecanismos de Controle de Repetição
1. **Esquema Estruturado JSON:** O Qwen local é compelido a responder com `risco` (uma frase) e `pergunta` (uma questão concreta).
2. **Detecção de Eco e N-Gramas:** Rejeição de respostas que copiem mais de 45% de sequências de 6 palavras do prompt de entrada.
3. **Verificação de Similaridade Histórica:** Respostas locais são comparadas com o histórico recente; similaridade acima de 85% dispara retentativa.
4. **Filtro de Idioma e Termos-Âncora:** Garantia de termos em português e presença de vocábulos relacionados ao tema da rodada.
5. **Contexto Enxuto:** Evitou-se sobrecarregar a janela de contexto do Qwen 1.5B com metacomentários, preservando foco e clareza argumentativa.
