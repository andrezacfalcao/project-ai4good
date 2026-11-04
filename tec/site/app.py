"""Site local do Atlas do Erro: roda o TrOCR, o SymPy e o Qwen sobre as imagens de teste e mostra os resultados.

Rodar a partir da raiz do repositório, com o Ollama ativo:
  tec/.venv/bin/streamlit run tec/site/app.py
"""
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import atlas  # noqa: E402

st.set_page_config(page_title="Atlas do Erro", page_icon="📓", layout="wide")

# ---------- as imagens de teste ----------
GAB_TEC = {  # tec/cadernos/README.md: transcrição esperada e primeira passagem incorreta
    "caderno-1.png": (["2x + 4 = 10", "2x = 10 + 4", "x = 7"], 2, "troca_sinal"),
    "caderno-2.png": (["3x - 6 = 9", "3x = 9 - 6", "x = 1"], 2, "troca_sinal"),
    "caderno-3.png": (["4x + 8 = 20", "4x = 20 + 8", "x = 7"], 2, "troca_sinal"),
}
CONJUNTOS = {
    "Cadernos do tec (3 imagens)": "tec",
    "Resoluções do piloto do exp (60 imagens)": "exp",
    "Enviar uma foto": "upload",
}


@st.cache_data
def casos(conjunto):
    if conjunto == "tec":
        return [{"nome": n, "caminho": str(RAIZ / "tec" / "cadernos" / n), "linhas": l, "linha_erro": k, "tipo": t,
                 "foto": "pauta" if n == "caderno-3.png" else "limpa"} for n, (l, k, t) in GAB_TEC.items()]
    gab = RAIZ / "exp" / "piloto" / "dados" / "gabarito.json"
    if conjunto == "exp" and gab.exists():
        return [{"nome": Path(c["imagem"]).name, "caminho": str(gab.parent / c["imagem"]), "linhas": c["linhas"],
                 "linha_erro": c["linha_erro"], "tipo": c["tipo"], "foto": c["foto"]}
                for c in json.loads(gab.read_text(encoding="utf-8"))]
    return []


@st.cache_resource(show_spinner="Carregando o TrOCR…")
def ocr():
    return atlas.carregar_ocr()


def norm(s):
    return "".join(s.lower().split())


def comparar(res, caso):
    """Confere o resultado com o gabarito da imagem."""
    if not caso:
        return None
    if caso["linha_erro"] is None:
        loc_ok = res["diagnostico"] == "sem_quebra"
    else:
        loc_ok = res["diagnostico"] == "quebra" and res["linha_quebra"] == caso["linha_erro"]
    exatas = sum(1 for i, l in enumerate(caso["linhas"]) if i < len(res["linhas"]) and norm(res["linhas"][i]) == norm(l))
    tipo_ok = None if caso["linha_erro"] is None or caso["tipo"] == "sem_erro" else res["categoria"] == caso["tipo"]
    return {"loc_ok": loc_ok, "tipo_ok": tipo_ok, "exatas": exatas, "total": len(caso["linhas"])}


def selo(ok):
    return "—" if ok is None else ("✅" if ok else "❌")


# ---------- barra lateral ----------
with st.sidebar:
    st.header("Configuração")
    modelos = atlas.modelos_instalados()
    if modelos:
        st.success(f"Ollama ativo · {len(modelos)} modelo(s) Qwen")
    else:
        st.error("Ollama não respondeu em localhost:11434. O OCR e o SymPy rodam; a pista, não.")
    padrao = modelos.index("qwen2.5:1.5b") if "qwen2.5:1.5b" in modelos else 0
    modelo = st.selectbox("Modelo da pista (passo 7)", modelos, index=padrao) if modelos else None
    recorte = st.radio("Recorte das linhas (passo 3)", ["vaos", "fixo"],
                       format_func=lambda r: "pelos vãos entre as linhas (flx)" if r == "vaos" else "três faixas fixas (tec)")
    lista_fixa = st.toggle("Lista fixa de categorias (flx)", value=True,
                           help="Desligado, usa o prompt original do tec, com categoria livre.")
    st.caption("Tudo roda nesta máquina. As imagens de teste são sintéticas: não são cadernos de alunos.")

st.title("📓 Atlas do Erro")
st.write("A foto de uma resolução entra; sai a linha em que o raciocínio quebrou e uma pista, sem a resposta.")

aba_uma, aba_todas, aba_sobre = st.tabs(["Rodar uma imagem", "Rodar o conjunto inteiro", "Sobre"])

# ---------- aba 1: uma imagem ----------
with aba_uma:
    nome_conj = st.radio("Imagens", list(CONJUNTOS), horizontal=True)
    conj = CONJUNTOS[nome_conj]
    caso, img = None, None
    if conj == "upload":
        arquivo = st.file_uploader("Foto da resolução (PNG ou JPG)", type=["png", "jpg", "jpeg"])
        if arquivo:
            img = atlas.abrir(arquivo)
            chave = f"upload:{arquivo.name}:{arquivo.size}"
    else:
        lista = casos(conj)
        if not lista:
            st.warning("Este conjunto não está no repositório.")
        else:
            rotulo = {c["nome"]: f"{c['nome']} · {c['tipo'].replace('_', ' ')} · {c['foto']}" for c in lista}
            nome = st.selectbox("Escolha a imagem", [c["nome"] for c in lista], format_func=rotulo.get)
            caso = next(c for c in lista if c["nome"] == nome)
            img = atlas.abrir(caso["caminho"])
            chave = f"{conj}:{nome}"

    if img is not None:
        col_img, col_res = st.columns([1, 1.3], gap="large")
        with col_img:
            st.image(img, caption="Entrada", width="stretch")
            if st.button("▶ Rodar o Atlas", type="primary", width="stretch"):
                with st.spinner("Recortando, lendo e conferindo…"):
                    st.session_state[chave] = atlas.rodar(ocr(), img, modelo, recorte, lista_fixa)
        res = st.session_state.get(chave)
        with col_res:
            if res is None:
                st.info("Clique em **Rodar o Atlas** para ver cada passo.")
            else:
                st.subheader("Passos 3 e 4 · recorte e leitura")
                if res["faixas"]:
                    for i, (f, l) in enumerate(zip(res["faixas"], res["linhas"]), 1):
                        a, b = st.columns([2, 1])
                        a.image(f, width="stretch")
                        b.code(l or "(vazio)", language=None)
                st.caption(f"{len(res['linhas'])} linha(s) lida(s) · {res['t_ocr']:.2f} s")

                st.subheader("Passo 5 · conferir a transcrição")
                texto = st.text_area("Uma linha da resolução por linha. Corrija o que foi mal lido e rode de novo.",
                                     "\n".join(res["linhas"]), key=f"txt:{chave}", height=120)
                if st.button("↻ Rodar de novo com esta transcrição"):
                    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
                    with st.spinner("Conferindo…"):
                        novo = atlas.rodar(None, None, modelo, recorte, lista_fixa, linhas=linhas)
                    novo["faixas"] = res["faixas"]
                    st.session_state[chave] = novo
                    st.rerun()

                st.subheader("Passo 6 · onde quebrou (SymPy)")
                if res["diagnostico"] == "quebra":
                    st.error(f"Quebra na **linha {res['linha_quebra']}**: "
                             f"`{res['linhas'][res['linha_quebra'] - 2]}` → `{res['linhas'][res['linha_quebra'] - 1]}`")
                elif res["diagnostico"] == "sem_quebra":
                    st.success("Nenhuma quebra: cada linha é equivalente à anterior.")
                else:
                    st.warning(f"Leitura inválida: {res['diag_texto']}. Confira a transcrição no passo 5.")

                st.subheader("Passo 7 · tipo do erro e pista (Qwen)")
                if res["diagnostico"] != "quebra":
                    st.caption("Sem quebra, o Qwen não é chamado.")
                elif not modelo:
                    st.caption("Sem o Ollama, não há pista.")
                else:
                    st.metric("Categoria", (res["categoria"] or "—").replace("_", " "))
                    st.info(res["pista"] or "(sem pista)")
                    if res["pista_da_valor"]:
                        st.warning("Atenção: a pista escreve um valor de x que não está na resolução.")
                st.caption(f"Tempo da foto à pista: {res['t_total']:.2f} s (sem a carga do modelo)")

                cmp = comparar(res, caso)
                if cmp:
                    st.subheader("Conferência com o gabarito")
                    esperado = "sem quebra" if caso["linha_erro"] is None else f"linha {caso['linha_erro']}"
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Linhas lidas exatas", f"{cmp['exatas']} de {cmp['total']}")
                    c2.metric("Quebra apontada", selo(cmp["loc_ok"]), help=f"Esperado: {esperado}")
                    c3.metric("Tipo do erro", selo(cmp["tipo_ok"]), help=f"Esperado: {caso['tipo'].replace('_', ' ')}")
                    st.caption("Transcrição esperada: " + " → ".join(f"`{l}`" for l in caso["linhas"]))

# ---------- aba 2: o conjunto inteiro ----------
with aba_todas:
    nome_todos = st.radio("Conjunto", [k for k, v in CONJUNTOS.items() if v != "upload"], horizontal=True, key="conj_todas")
    lista = casos(CONJUNTOS[nome_todos])
    st.write(f"{len(lista)} imagens. Cada uma passa pelo recorte, pelo TrOCR, pelo SymPy e, se houver quebra, pelo Qwen.")
    if lista and st.button("▶ Rodar todas", type="primary"):
        barra, linhas_tab = st.progress(0.0, text="Começando…"), []
        modelo_ocr = ocr()
        for i, c in enumerate(lista, 1):
            r = atlas.rodar(modelo_ocr, atlas.abrir(c["caminho"]), modelo, recorte, lista_fixa)
            k = comparar(r, c)
            linhas_tab.append({
                "imagem": c["nome"], "tipo esperado": c["tipo"], "foto": c["foto"],
                "linhas lidas exatas": f"{k['exatas']}/{k['total']}",
                "quebra esperada": c["linha_erro"] or "—", "quebra apontada": r["linha_quebra"] or r["diagnostico"],
                "quebra certa": selo(k["loc_ok"]), "categoria": r["categoria"] or "—", "tipo certo": selo(k["tipo_ok"]),
                "pista com valor de x": "⚠️" if r["pista_da_valor"] else "", "pista": r["pista"] or "",
                "tempo (s)": round(r["t_total"], 2), "_loc": k["loc_ok"], "_tipo": k["tipo_ok"],
                "_ex": k["exatas"], "_tot": k["total"]})
            barra.progress(i / len(lista), text=f"{i} de {len(lista)} · {c['nome']}")
        st.session_state["todas"] = (nome_todos, linhas_tab)
    if st.session_state.get("todas") and st.session_state["todas"][0] == nome_todos:
        df = pd.DataFrame(st.session_state["todas"][1])
        tipos = df["_tipo"].dropna()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Linhas lidas exatas", f"{100 * df['_ex'].sum() / df['_tot'].sum():.0f}%")
        m2.metric("Quebra certa", f"{100 * df['_loc'].mean():.0f}%")
        m3.metric("Tipo do erro certo", f"{100 * tipos.mean():.0f}%" if len(tipos) else "—")
        m4.metric("Tempo médio", f"{df['tempo (s)'].mean():.2f} s")
        por_foto = df.groupby("foto")["_loc"].mean().mul(100).round().astype(int).astype(str) + "%"
        st.caption("Quebra certa por tipo de foto: " + " · ".join(f"{k}: {v}" for k, v in por_foto.items()))
        visivel = df.drop(columns=[c for c in df.columns if c.startswith("_")])
        st.dataframe(visivel, width="stretch", hide_index=True)
        st.download_button("Baixar os resultados (CSV)", visivel.to_csv(index=False).encode("utf-8"),
                           file_name="atlas_resultados.csv", mime="text/csv")
        st.caption("Uma execução, sem intervalo de confiança: para as métricas do piloto, veja exp/piloto/.")

# ---------- aba 3: sobre ----------
with aba_sobre:
    st.markdown("""
**O que o site faz.** Repete o caminho de `tec/ler_caderno.py`: recorta a foto em linhas (passo 3), lê cada
linha com o TrOCR (passo 4), acha no SymPy a primeira linha que não é equivalente à anterior (passo 6) e pede
ao Qwen, pelo Ollama local, o tipo do erro e uma pista sem a resposta (passo 7). A caixa do passo 5 deixa
você corrigir a transcrição, como o aluno faria, e rodar de novo.

**As opções.** O recorte "pelos vãos" e a "lista fixa de categorias" são as versões do fluxograma (`flx`);
"três faixas fixas" e a categoria livre são as do `tec`.

**O que ele não prova.** As imagens são sintéticas, digitadas em fontes que imitam letra à mão. O TrOCR usado
é o modelo para texto impresso. A saída do Qwen pode mudar entre execuções. Para os números com intervalo de
confiança e as ablações, veja o piloto do `exp`.
""")
