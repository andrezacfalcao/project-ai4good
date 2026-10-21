// Gera cp02_slides.pptx (com notas de fala) e FALA_APRESENTACAO.md a partir do mesmo conteúdo.
// uso: NODE_PATH=<pasta com node_modules/pptxgenjs> node criar_slides.js
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.APPLY_THEME || "./apply_theme.js");

const THEME = {
  name: "CP02 ModernTCN",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2A41", lt1: "FFFFFF", dk2: "0B1F3A", lt2: "EEF3F6",
    accent1: "1F8A8A", accent2: "F2A541", accent3: "C8553D",
    accent4: "5B7C99", accent5: "8FB8C9", accent6: "2E4A66",
    hlink: "1F8A8A", folHlink: "5B7C99",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.title = "CP02 · Reprodução e modificação do ModernTCN";
pres.author = "Andreza Maria Coutinho Falcão";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "TITULO", background: { color: "0B1F3A" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.5, w: 8.8, h: 1.5, fontFace: "Cambria", fontSize: 38, bold: true, color: "FFFFFF", margin: 0, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.2, w: 8.8, h: 1.2, fontSize: 18, color: "8FB8C9", margin: 0, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTEUDO", background: { color: "FFFFFF" },
  slideNumber: { x: 9.2, y: 5.15, w: 0.5, h: 0.3, fontSize: 10, color: "5B7C99", align: "right" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 8.8, h: 0.8, fontFace: "Cambria", fontSize: 32, bold: true, color: "0B1F3A", margin: 0, valign: "middle", align: "left" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "FECHO", background: { color: "0B1F3A" }, slideNumber: { x: 9.2, y: 5.15, w: 0.5, h: 0.3, fontSize: 10, color: "8FB8C9", align: "right" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 8.8, h: 0.8, fontFace: "Cambria", fontSize: 32, bold: true, color: "FFFFFF", margin: 0, valign: "middle", align: "left" }, text: "" } },
  ],
});

const falas = [];
const FIG = path.join(__dirname, "figuras");
const card = (s, x, y, w, h, fill = "EEF3F6") =>
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.08 });
const txt = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, fontFace: "Calibri", color: "1B2A41" }, o));
const stat = (s, x, y, w, big, small, color = "1F8A8A", bg = "EEF3F6") => {
  card(s, x, y, w, 1.25, bg);
  txt(s, big, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.7, fontSize: 36, bold: true, fontFace: "Cambria", color, valign: "middle" });
  txt(s, small, { x: x + 0.15, y: y + 0.8, w: w - 0.3, h: 0.4, fontSize: 13, color: "1B2A41", valign: "top" });
};
const arrow = (s, x1, y, x2) => s.addShape(pres.ShapeType.line, { x: x1, y, w: x2 - x1, h: 0, line: { color: "5B7C99", width: 2, endArrowType: "triangle" } });
const box = (s, x, y, w, h, t, fill, color = "FFFFFF", size = 14) => {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.08 });
  txt(s, t, { x: x + 0.1, y, w: w - 0.2, h, fontSize: size, bold: true, color, align: "center", valign: "middle" });
};
const slide = (master, title, fala, section) => {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  if (title) s.addText(title, { placeholder: "title" });
  s.addNotes(fala); falas.push({ title: title || "Abertura", fala });
  return s;
};

// 1 · abertura
pres.addSection({ title: "Abertura" });
{
  const s = pres.addSlide({ masterName: "TITULO", sectionTitle: "Abertura" });
  s.addText("Reprodução e modificação do ModernTCN", { placeholder: "title" });
  s.addText("CP02 · Tópicos Avançados em IA\nAndreza Maria Coutinho Falcão", { placeholder: "body" });
  const f = "Esta é a CP02: reproduzir um modelo de aprendizado profundo da literatura e modificar a arquitetura dele. Escolhi o ModernTCN, um artigo do ICLR de 2024. Vou mostrar que consegui reproduzir os resultados do artigo, qual modificação testei e, principalmente, que ela não melhorou o modelo, e por quê.";
  s.addNotes(f); falas.push({ title: "Abertura", fala: f });
}

// 2 · artigo
pres.addSection({ title: "Artigo base" });
{
  const s = slide("CONTEUDO", "O artigo base: ModernTCN", "O artigo é o ModernTCN, de Luo e Wang, publicado no ICLR 2024. É uma rede convolucional pura, e atende ao que a atividade pede: é de 2024, dentro do exigido (2023 em diante), usa CNN e tem código aberto sob licença MIT. Os autores publicam os scripts com todos os hiperparâmetros, e a base de dados é pública. Isso importa porque só assim dá para reproduzir de verdade. Eu tentei antes com outro artigo, o HCBiLSTM, mas ele não publica código, então troquei.", "Artigo base");
  const itens = [
    ["ICLR 2024", "a atividade exige artigos de 2023 em diante"],
    ["CNN pura", "sem recorrência nem atenção"],
    ["Código aberto", "GitHub oficial, licença MIT"],
    ["Dados públicos", "ETT: temperatura de transformadores"],
  ];
  itens.forEach(([a, b], i) => {
    const x = 0.6 + (i % 2) * 4.5, y = 1.5 + Math.floor(i / 2) * 1.6;
    card(s, x, y, 4.2, 1.35);
    txt(s, a, { x: x + 0.25, y: y + 0.2, w: 3.7, h: 0.5, fontSize: 22, bold: true, fontFace: "Cambria", color: "1F8A8A" });
    txt(s, b, { x: x + 0.25, y: y + 0.75, w: 3.7, h: 0.4, fontSize: 16 });
  });
  txt(s, "Luo e Wang. ModernTCN: A Modern Pure Convolution Structure for General Time Series Analysis. ICLR 2024.", { x: 0.6, y: 4.85, w: 8.2, h: 0.4, fontSize: 11, color: "5B7C99" });
}

// 3 · como funciona
{
  const s = slide("CONTEUDO", "Como o ModernTCN funciona", "A tarefa é prever as próximas 96 horas de sete medições de um transformador elétrico, olhando as 336 horas anteriores. O modelo corta cada medição em 84 pedaços, os patches. Cada pedaço passa por um bloco com três partes: uma convolução com kernel grande, de 51 passos, que olha bem para trás; uma rede que mistura as características de cada variável; e outra que mistura as variáveis entre si. No fim, uma camada linear dá a previsão. O ponto-chave é que esses filtros de kernel grande são fixos: tratam toda entrada do mesmo jeito.", "Artigo base");
  box(s, 0.6, 1.9, 1.7, 1.2, "Série\n336 h × 7 variáveis", "2E4A66", "FFFFFF", 13);
  arrow(s, 2.35, 2.5, 2.75);
  box(s, 2.8, 1.9, 1.7, 1.2, "84 patches\npor variável", "5B7C99", "FFFFFF", 13);
  arrow(s, 4.55, 2.5, 4.95);
  card(s, 5.0, 1.45, 2.7, 2.1, "EEF3F6");
  txt(s, "Bloco ModernTCN", { x: 5.0, y: 1.5, w: 2.7, h: 0.4, fontSize: 14, bold: true, color: "0B1F3A", align: "center" });
  box(s, 5.15, 1.95, 2.4, 0.45, "Convolução kernel 51", "1F8A8A", "FFFFFF", 12);
  box(s, 5.15, 2.5, 2.4, 0.45, "FFN por variável", "1F8A8A", "FFFFFF", 12);
  box(s, 5.15, 3.05, 2.4, 0.4, "FFN entre variáveis", "1F8A8A", "FFFFFF", 12);
  arrow(s, 7.75, 2.5, 8.1);
  box(s, 8.15, 1.9, 1.3, 1.2, "Previsão\n96 h", "0B1F3A", "FFFFFF", 13);
  txt(s, "Os filtros de kernel grande são pesos fixos: tratam toda entrada do mesmo jeito.", { x: 0.6, y: 4.0, w: 8.8, h: 0.5, fontSize: 18, italic: true, color: "1F8A8A" });
}

// 4 · reprodução
pres.addSection({ title: "Reprodução" });
{
  const s = slide("CONTEUDO", "Reprodução: o artigo fecha", "Primeiro reproduzi o baseline, sem mudar nada: usei o código oficial com o comando exato do artigo, para a base ETTh2 e horizonte de 96 horas, com as cinco sementes que o artigo usa. O artigo reporta erro quadrático médio de 0,263. Eu obtive 0,2645, com desvio de 0,0006. A diferença é de 0,0015, menos de 1 por cento. Isso é uma boa notícia: significa que o código e o protocolo estão certos, e que qualquer diferença depois vem da minha modificação. Fiz só dois ajustes de compatibilidade, que não mudam o modelo: uma função do NumPy 2 e o uso da GPU do Mac.", "Reprodução");
  stat(s, 0.6, 1.5, 2.7, "0,263", "MSE reportado no artigo", "5B7C99");
  stat(s, 3.65, 1.5, 2.7, "0,2645", "MSE reproduzido, 5 sementes", "1F8A8A");
  stat(s, 6.7, 1.5, 2.7, "0,6%", "diferença para o artigo", "F2A541".replace("F2A541", "C8553D"));
  txt(s, [
    { text: "Código oficial sem alterar hiperparâmetros", options: { bullet: true, breakLine: true } },
    { text: "Base ETTh2, prever 96 h a partir de 336 h", options: { bullet: true, breakLine: true } },
    { text: "Sementes 2021 a 2025, Adam 1e-4, parada antecipada", options: { bullet: true } },
  ], { x: 0.6, y: 3.2, w: 8.8, h: 1.4, fontSize: 16, paraSpaceAfter: 6 });
}

// 5 · modificação
pres.addSection({ title: "Modificação" });
{
  const s = slide("CONTEUDO", "A modificação: atenção sobre patches", "A minha hipótese é que, como os filtros convolucionais são fixos, uma camada de atenção poderia deixar o modelo ponderar o passado conforme a entrada, o que ajudaria numa série que muda ao longo do tempo. Então acrescentei, no fim de cada bloco, uma auto-atenção sobre os patches. Para não estragar o modelo, o ganho dessa camada, o gamma, começa em zero. Assim, no início, o modelo é idêntico ao oficial, e qualquer diferença nos resultados foi aprendida. Eu testei isso: com gamma igual a zero, a saída é exatamente a mesma. A mudança custa 22 mil parâmetros a mais, 3,4 por cento.", "Modificação");
  box(s, 0.6, 1.6, 2.2, 0.9, "Bloco ModernTCN\n(convoluções)", "1F8A8A", "FFFFFF", 14);
  arrow(s, 2.85, 2.05, 3.3);
  box(s, 3.35, 1.6, 2.6, 0.9, "Atenção sobre patches\n× γ (começa em 0)", "F2A541", "0B1F3A", 14);
  arrow(s, 6.0, 2.05, 6.45);
  box(s, 6.5, 1.6, 1.6, 0.9, "Cabeça\nlinear", "0B1F3A", "FFFFFF", 14);
  txt(s, "x_novo = x + γ · Atenção( LayerNorm(x) + posição )", { x: 0.6, y: 2.85, w: 8.8, h: 0.5, fontSize: 20, bold: true, fontFace: "Cambria", color: "0B1F3A" });
  txt(s, [
    { text: "Hipótese: filtros fixos não se adaptam à entrada; a atenção sim", options: { bullet: true, breakLine: true } },
    { text: "γ = 0 no início: o modelo começa idêntico ao oficial (testado)", options: { bullet: true, breakLine: true } },
    { text: "Custo: 681.989 parâmetros contra 659.844 (+3,4%)", options: { bullet: true } },
  ], { x: 0.6, y: 3.5, w: 8.8, h: 1.4, fontSize: 16, paraSpaceAfter: 6 });
}

// 6 · resultado
pres.addSection({ title: "Resultados" });
{
  const s = slide("CONTEUDO", "Resultado: a atenção não ajudou", "Aqui está a comparação, com as mesmas cinco sementes e o mesmo protocolo. O modelo modificado teve erro um pouco maior que o baseline: 0,2654 contra 0,2645. A diferença é pequena, mas consistente: em quatro das cinco sementes o modificado foi pior, e na outra empatou. Ou seja, a hipótese não se confirmou. Isso é um resultado negativo, e a atividade pede modificar, retreinar e medir, não que a modificação melhore.", "Resultados");
  const h = { bold: true, color: "FFFFFF", fill: { color: "0B1F3A" }, align: "center", fontSize: 15 };
  const c = (t, o = {}) => ({ text: t, options: Object.assign({ align: "center", fontSize: 15, color: "1B2A41" }, o) });
  const l = (t) => ({ text: t, options: { bold: true, align: "left", fontSize: 15, color: "1B2A41" } });
  s.addTable([
    [{ text: "", options: h }, { text: "Artigo", options: h }, { text: "Reproduzido", options: h }, { text: "Modificado", options: h }],
    [l("MSE"), c("0,263"), c("0,2645 ± 0,0006"), c("0,2654 ± 0,0007", { bold: true, color: "C8553D" })],
    [l("MAE"), c("0,332"), c("0,3331 ± 0,0004"), c("0,3337 ± 0,0007", { bold: true, color: "C8553D" })],
    [l("Épocas até parar"), c("—"), c("61,4"), c("46,2")],
    [l("Parâmetros"), c("—"), c("659.844"), c("681.989")],
  ], { x: 0.6, y: 1.5, w: 8.8, colW: [2.6, 1.8, 2.2, 2.2], rowH: 0.5, border: { type: "solid", color: "C9D6DF", pt: 1 }, fill: { color: "FFFFFF" }, margin: [0, 0.1, 0, 0.1] });
  txt(s, "ETTh2, horizonte 96, dados padronizados, média e desvio de 5 sementes. Menor é melhor.", { x: 0.6, y: 4.2, w: 8.8, h: 0.4, fontSize: 12, color: "5B7C99" });
}

// 7 · por que
pres.addSection({ title: "Análise" });
{
  const s = slide("CONTEUDO", "Por quê? O modelo ignorou a atenção", "Para entender por que, olhei o gamma que o modelo aprendeu. Ele partiu de zero e ficou em torno de 0,02, com sinal ora positivo, ora negativo: a rede quase não usou a atenção. Por isso as previsões dos dois modelos são quase idênticas. Janela a janela, o modificado só vence em 39,9 por cento dos casos. Nesta figura, a temperatura do óleo em três janelas reais do teste: a que a modificação mais ajuda, a que mais atrapalha, e a pior do baseline. As duas curvas acertam o ciclo diário, o formato, mas erram o nível, e erram igual.", "Análise");
  stat(s, 0.6, 1.4, 2.7, "γ ≈ 0,02", "ganho aprendido: a atenção quase não é usada", "C8553D");
  stat(s, 3.65, 1.4, 2.7, "39,9%", "das janelas em que o modificado vence", "1F8A8A");
  stat(s, 6.7, 1.4, 2.7, "+0,0009", "diferença de MSE a favor do baseline", "5B7C99");
  s.addImage({ path: path.join(FIG, "cp02_janelas_exemplo.png"), x: 0.8, y: 2.85, w: 8.4, h: 2.37, altText: "Previsão da temperatura do óleo em três janelas de teste: real, baseline e modificado quase idênticos." });
}

// 8 · variável / nível
{
  const s = slide("CONTEUDO", "O erro é de nível, não de formato", "Por variável, o erro muda muito pouco com a modificação: as mais difíceis são MULL e HUFL, e nenhuma muda mais de 0,003. Também vi que 4 por cento das janelas concentram o erro, e nelas os dois modelos dão o mesmo resultado, cerca de quatro vezes pior que nas demais. Minha interpretação, que é uma hipótese e eu não testei, é que existe uma mudança de regime entre o período de treino e o de teste. Se for isso, o limite está nos dados, e não na capacidade do modelo, que é o que a atenção acrescentaria.", "Análise");
  s.addImage({ path: path.join(FIG, "cp02_mse_por_variavel.png"), x: 0.6, y: 1.45, w: 5.4, h: 2.47, altText: "MSE por variável, baseline e modificado, praticamente iguais." });
  txt(s, [
    { text: "4% das janelas concentram o erro", options: { bullet: true, breakLine: true } },
    { text: "Nelas, os dois modelos são iguais", options: { bullet: true, breakLine: true } },
    { text: "Os modelos acertam o ciclo diário e erram o nível", options: { bullet: true } },
  ], { x: 6.3, y: 1.55, w: 3.2, h: 2.3, fontSize: 15, paraSpaceAfter: 8 });
  txt(s, "Hipótese, não testada: mudança de regime entre treino e teste.", { x: 0.6, y: 4.2, w: 8.8, h: 0.5, fontSize: 16, italic: true, color: "1F8A8A" });
}

// 9 · conclusão
pres.addSection({ title: "Fecho" });
{
  const s = slide("FECHO", "Conclusão", "Em resumo: reproduzi o ModernTCN com erro de menos de 1 por cento em relação ao artigo. A modificação com atenção não melhorou o modelo, e eu consegui mostrar por quê: o ganho aprendido ficou perto de zero. Como limitações: testei uma base e um horizonte, e a modificação tem um único desenho. Como próximos passos, testar outras bases e horizontes, e atacar a mudança de nível com técnicas de normalização adaptativa.", "Fecho");
  const itens = [
    ["Reproduzido", "MSE 0,2645 contra 0,263 do artigo"],
    ["Resultado negativo", "a atenção não melhorou (0,2654), e γ ≈ 0,02 mostra por quê"],
    ["Próximos passos", "outras bases e horizontes; lidar com mudança de nível"],
  ];
  itens.forEach(([a, b], i) => {
    const y = 1.5 + i * 1.15;
    s.addShape(pres.ShapeType.roundRect, { x: 0.6, y, w: 8.8, h: 0.95, fill: { color: "2E4A66" }, line: { color: "2E4A66", width: 0 }, rectRadius: 0.08 });
    txt(s, a, { x: 0.85, y, w: 2.7, h: 0.95, fontSize: 18, bold: true, fontFace: "Cambria", color: "F2A541", valign: "middle" });
    txt(s, b, { x: 3.6, y, w: 5.6, h: 0.95, fontSize: 16, color: "FFFFFF", valign: "middle" });
  });
  txt(s, "Limites: uma base (ETTh2), um horizonte (96), um único desenho de modificação.", { x: 0.6, y: 4.85, w: 8.2, h: 0.35, fontSize: 12, color: "8FB8C9" });
}

// 10 · checklist
{
  const s = slide("CONTEUDO", "O que a atividade pede e onde está", "Para fechar, o que a atividade pede e onde está cada evidência no repositório. A pasta tem o CONTEXT ponto md; os dados são os do artigo; o baseline roda com um script e tem log por semente; e a modificação está marcada no código, com um arquivo de diferenças que mostra exatamente o que mudou em relação ao oficial. O relatório em LaTeX está no Overleaf, com trabalhos relacionados, tabela comparativa e análise qualitativa.", "Fecho");
  const h = { bold: true, color: "FFFFFF", fill: { color: "0B1F3A" }, fontSize: 13 };
  const r = (a, b) => [{ text: a, options: { bold: true, fontSize: 12, color: "1B2A41" } }, { text: b, options: { fontSize: 12, color: "1B2A41" } }];
  s.addTable([
    [{ text: "Item", options: h }, { text: "Evidência", options: h }],
    r("Subrepositório e CONTEXT.md", "cp02_arquitetura/CONTEXT.md"),
    r("Dataset do artigo", "data/ETT-small (ETTh2, base pública ETDataset)"),
    r("Inferência funcional", "pred.npy de cada semente + janelas reais na análise"),
    r("Baseline as-is", "rodar_baseline.sh e logs: MSE 0,2645 contra 0,263"),
    r("Modificação arquitetural", "PatchAttention, marcada no código; DIFF_vs_oficial.patch"),
    r("Relatório (arq·p)", "report-arch.tex no Overleaf: relacionados, tabela, análise"),
  ], { x: 0.6, y: 1.4, w: 8.8, colW: [3.0, 5.8], rowH: 0.45, border: { type: "solid", color: "C9D6DF", pt: 1 }, fill: { color: "FFFFFF" }, margin: [0, 0.1, 0, 0.1] });
}

(async () => {
  const out = path.join(__dirname, "cp02_slides.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  const md = ["# Roteiro de fala · CP02 (ModernTCN)", "", "Um bloco por slide, em ordem. O mesmo texto está nas notas do `cp02_slides.pptx`.", ""]
    .concat(falas.map((f, i) => `## ${i + 1} · ${f.title}\n\n${f.fala}\n`)).join("\n");
  fs.writeFileSync(path.join(__dirname, "FALA_APRESENTACAO.md"), md);
  console.log("ok", out);
})();
