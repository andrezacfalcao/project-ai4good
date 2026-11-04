// Gera sem1/sem1.pptx: 5 slides com notas de apresentador para o seminário preliminar.
// Rodar a partir da raiz, com o pptxgenjs instalado (npm install pptxgenjs@3.12.0):
//   node sem1/gerar_slides.js
const path = require("path");
const pptxgen = require("pptxgenjs");

const AQUI = __dirname;
const img = (n) => path.join(AQUI, "imagens", n);

const THEME = {
  name: "Atlas do Erro",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1D2B4A", lt1: "FFFFFF", dk2: "2E3A55", lt2: "EEF2F8",
    accent1: "D7263D", accent2: "2F6FB3", accent3: "2E8B57", accent4: "F2B134",
    accent5: "5B6475", accent6: "9AA5B8", hlink: "2F6FB3", folHlink: "6D4C9F",
  },
};
const HEX = { tinta: "1D2B4A", caneta: "D7263D", verde: "2E8B57", cinza: "5B6475", papel: "EEF2F8", branco: "FFFFFF" };

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625 pol.
  pres.author = "Andreza Maria Coutinho Falcão";
  pres.title = "Atlas do Erro · seminário preliminar";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "CONTEUDO",
    background: { color: C.background1 },
    objects: [
      { text: { text: "Andreza Falcão · Atlas do Erro", options: { x: 0.5, y: 5.2, w: 5, h: 0.3, fontSize: 10, color: C.accent5, isTextBox: true } } },
    ],
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
    placeholders: [],
  });
  pres.defineSlideMaster({ title: "ESCURO", background: { color: C.text1 }, objects: [] });

  const titulo = (s, t, cor) => s.addText(t, {
    x: 0.5, y: 0.3, w: 9, h: 0.75, fontFace: THEME.headFontFace, fontSize: 26, bold: true,
    color: cor || C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: "titulo",
  });
  const legenda = (s, t, x, y, w) => s.addText(t, {
    x, y, w, h: 0.3, fontSize: 11, color: C.accent5, margin: 0, isTextBox: true, objectName: "legenda",
  });
  const marca = (s, x, y, w, h) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.12, fill: { type: "none" }, line: { color: C.accent1, width: 2.5 }, objectName: "marca de caneta",
  });

  // ---------- 1 · a ideia ----------
  pres.addSection({ title: "A ideia" });
  let s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "A ideia" });
  titulo(s, "O aluno resolve. A IA aponta onde quebrou");
  s.addImage({ path: img("caderno.png"), x: 0.5, y: 1.35, w: 4.4, h: 2.64, altText: "Foto de teste de uma resolução: 2x + 4 = 10, 2x = 10 + 4, x = 7" });
  marca(s, 0.55, 2.2, 2.75, 0.85);
  s.addText("a linha que quebrou", { x: 3.35, y: 2.42, w: 1.6, h: 0.4, fontSize: 12, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  s.addImage({ path: img("atlas_pista.png"), x: 5.3, y: 1.35, w: 4.2, h: 2.86, altText: "Protótipo do Atlas: categoria troca de sinal, pista sem a resposta e conferência com o gabarito" });
  legenda(s, "a foto do caderno (imagem de teste)", 0.5, 4.1, 4.4);
  legenda(s, "o protótipo rodando: o tipo do erro e a pista, sem a resposta", 5.3, 4.3, 4.2);
  s.addNotes(
    "Pensa num aluno do sétimo ano fazendo a lista de equação em casa. Ele trava numa conta, tira foto com o Photomath ou com o ChatGPT, e a resposta aparece pronta. Ele copia e entrega. Só que na prova não tem IA, e aí ele não sabe fazer.\n\n" +
    "E isso já foi medido: num estudo com quase mil alunos do ensino médio, quem estudou com a IA dando a resposta tirou 17% menos na prova sem a IA.\n\n" +
    "O Atlas do Erro faz o contrário. O aluno continua resolvendo no caderno, à mão. Ele tira uma foto, a IA lê a resolução linha por linha e mostra só onde o raciocínio quebrou, com uma pista. A resposta ela não dá.\n\n" +
    "Aqui é o protótipo rodando de verdade. Ele achou o erro na linha 2, o sinal trocado quando o 4 passou para o outro lado, e a pista só manda revisar o sinal. Quem corrige é o aluno."
  );

  // ---------- 2 · o produto mais próximo ----------
  pres.addSection({ title: "O produto mais próximo" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "O produto mais próximo" });
  titulo(s, "Photomath: lê a foto e entrega a resposta");
  s.addImage({ path: img("photomath.png"), x: 0.5, y: 1.35, w: 5.0, h: 2.5, altText: "Imagem oficial do Photomath: a câmera do celular lendo a equação 3x + 4 = 8" });
  s.addText([{ text: "photomath.com", options: { hyperlink: { url: "https://photomath.com/" } } }, { text: " · imagem oficial do app" }],
    { x: 0.5, y: 3.95, w: 5.0, h: 0.3, fontSize: 11, color: C.accent5, margin: 0, isTextBox: true });
  const linha = (y, ok, texto) => {
    s.addShape(pres.shapes.OVAL, { x: 5.9, y, w: 0.5, h: 0.5, fill: { color: ok ? C.accent3 : C.accent1 }, line: { type: "none" } });
    s.addText(ok ? "✓" : "✕", { x: 5.9, y, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(texto, { x: 6.55, y: y - 0.1, w: 3.0, h: 0.7, fontSize: 15, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  };
  linha(1.45, true, "lê a conta pela câmera, até escrita à mão");
  linha(2.3, false, "entrega a solução inteira, passo a passo");
  linha(3.15, false, "lê o exercício, não a resolução do aluno");
  marca(s, 5.8, 2.2, 3.8, 1.55);
  s.addNotes(
    "O produto que chega mais perto é o Photomath, que hoje é do Google. Escolhi ele porque é o que o aluno já usa: aponta a câmera para a conta e ele lê na hora, e lê bem, até letra à mão.\n\n" +
    "O problema é o que ele faz depois. Ele resolve a conta inteira, passo a passo. Ele lê o exercício, não o que o aluno escreveu. Então ele não diz em que linha o aluno errou, ele mostra o caminho certo pronto. Para quem quer aprender, isso é a resposta pronta de novo.\n\n" +
    "Eu também tentei derrubar a minha ideia com o ChatGPT com visão. Ele até acha o erro se você pedir, mas se o aluno insistir, ele dá o resultado. E os dois mandam a foto para a nuvem."
  );

  // ---------- 3 · o artigo mais próximo ----------
  pres.addSection({ title: "O artigo mais próximo" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "O artigo mais próximo" });
  titulo(s, "O artigo mais próximo: ScratchMath");
  s.addImage({ path: img("song_2026_p1.png"), x: 0.5, y: 1.2, w: 2.3, h: 3.83, altText: "Primeira página do artigo Can MLLMs Read Students' Minds?" });
  s.addText([
    { text: "Can MLLMs Read Students' Minds? Unpacking Multimodal Error Analysis in Handwritten Math", options: { italic: true, breakLine: true } },
    { text: "Song et al. · AIED 2026 · artigo completo nos anais (LNCS) · ", options: { fontSize: 12, color: C.accent5 } },
    { text: "doi.org/10.1007/978-3-032-29744-0_8", options: { fontSize: 12, hyperlink: { url: "https://doi.org/10.1007/978-3-032-29744-0_8" } } },
  ], { x: 3.2, y: 1.2, w: 6.3, h: 1.1, fontSize: 15, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  const numero = (x, grande, pequeno) => {
    s.addText(grande, { x, y: 2.65, w: 2.0, h: 0.8, fontFace: THEME.headFontFace, fontSize: 36, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(pequeno, { x, y: 3.45, w: 2.0, h: 0.75, fontSize: 13, color: C.accent5, margin: 0, valign: "top", isTextBox: true });
  };
  numero(3.2, "1.720", "rascunhos à mão de alunos do fundamental");
  numero(5.35, "16", "modelos multimodais testados");
  numero(7.5, "longe", "dos especialistas, pior em ler a letra");
  marca(s, 7.35, 2.55, 2.2, 1.75);
  s.addNotes(
    "Na ciência, o mais próximo é esse artigo da AIED deste ano, que é uma das conferências principais de IA na educação. É artigo completo.\n\n" +
    "Eles juntaram 1.720 rascunhos de verdade, feitos à mão por alunos do fundamental na China, e pediram para 16 modelos explicarem e classificarem o erro de cada um. É quase a minha tarefa.\n\n" +
    "E o resultado é que os modelos ficaram bem longe dos especialistas, e o pior foi justamente ler a letra e seguir o raciocínio do aluno. Os modelos abertos, que são os que dariam para rodar num celular, foram os mais fracos.\n\n" +
    "Para mim isso é um alerta: ler o caderno é o ponto fraco. E foi exatamente onde o meu piloto quebrou, como eu mostro agora."
  );

  // ---------- 4 · o que só a minha faz ----------
  pres.addSection({ title: "O que só a minha faz" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "O que só a minha faz" });
  titulo(s, "O que só o Atlas faz, e a pergunta");
  const cartao = (y, rotulo, texto) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 5.2, h: 1.45, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" } });
    s.addText(rotulo, { x: 0.75, y: y + 0.15, w: 4.8, h: 0.35, fontSize: 13, bold: true, color: C.accent2, margin: 0, isTextBox: true });
    s.addText(texto, { x: 0.75, y: y + 0.5, w: 4.8, h: 0.85, fontSize: 16, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  };
  cartao(1.25, "para o aluno", "lê o caderno de papel e dá só a pista, no próprio aparelho, sem internet");
  cartao(2.9, "para a ciência", "um sistema pequeno, local, acha a linha do erro como o professor, em 8 de cada 10?");
  s.addText("72%", { x: 6.2, y: 1.25, w: 3.3, h: 0.85, fontFace: THEME.headFontFace, fontSize: 44, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  s.addText("achou a linha do erro no piloto, abaixo da meta de 80%", { x: 6.2, y: 2.1, w: 3.3, h: 0.6, fontSize: 13, color: C.accent5, margin: 0, valign: "top", isTextBox: true });
  s.addText("90% → 64%", { x: 6.2, y: 2.9, w: 3.3, h: 0.85, fontFace: THEME.headFontFace, fontSize: 36, bold: true, color: C.text1, margin: 0, isTextBox: true });
  s.addText("linhas lidas certo, sem pauta e com pauta", { x: 6.2, y: 3.75, w: 3.3, h: 0.6, fontSize: 13, color: C.accent5, margin: 0, valign: "top", isTextBox: true });
  marca(s, 6.05, 1.15, 3.45, 1.6);
  legenda(s, "piloto com 60 resoluções de teste, sintéticas", 6.2, 4.5, 3.3);
  s.addNotes(
    "Nenhum trabalho que eu achei faz as três coisas juntas: ler o caderno de papel, apontar só a linha que quebrou sem dar a resposta, e rodar no próprio aparelho, sem mandar a foto do aluno para fora. Esse é o diferencial para o aluno.\n\n" +
    "A pergunta científica é essa: um sistema pequeno, rodando local, acha a linha do erro como o professor acharia, em pelo menos 8 de cada 10 resoluções?\n\n" +
    "E a resposta pode ser não. No meu piloto, com 60 resoluções de teste, ele achou em 72%, abaixo da meta. Com a folha pautada, a leitura caiu de 90% para 64% das linhas. E o modelo que dá o tipo do erro chamou tudo de troca de sinal.\n\n" +
    "Então, hoje, com imagem de teste, a resposta é não. É por isso que o experimento com caderno de verdade importa."
  );

  // ---------- 5 · fecho ----------
  pres.addSection({ title: "Fecho" });
  s = pres.addSlide({ masterName: "ESCURO", sectionTitle: "Fecho" });
  s.addText("A IA não pensa pelo aluno. Ela mostra onde ele parou.", {
    x: 0.5, y: 1.0, w: 4.8, h: 2.4, fontFace: THEME.headFontFace, fontSize: 32, bold: true, color: C.background1, margin: 0, valign: "middle", isTextBox: true,
  });
  s.addImage({ path: img("caderno.png"), x: 5.6, y: 1.2, w: 3.9, h: 2.34, altText: "A mesma foto de teste do caderno" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.65, y: 1.95, w: 2.45, h: 0.78, rectRadius: 0.12, fill: { type: "none" }, line: { color: HEX.caneta, width: 3 } });
  s.addText("Andreza Falcão · AI4Good · UFRPE", { x: 0.5, y: 4.7, w: 6, h: 0.3, fontSize: 11, color: C.accent6, margin: 0, isTextBox: true });
  s.addNotes(
    "Então é isso. O Photomath e o ChatGPT pensam pelo aluno. O Atlas devolve o raciocínio para ele: mostra onde ele parou, e quem termina a conta continua sendo o aluno."
  );

  const saida = path.join(AQUI, "sem1.pptx");
  await pres.writeFile({ fileName: saida });
  try {
    const { applyTheme } = require(process.env.APPLY_THEME);
    await applyTheme(saida, THEME);
  } catch (e) {
    console.log("tema não aplicado:", e.message);
  }
  console.log("ok:", saida);
}

main();
