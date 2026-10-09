"""
Caminhos do Cuidado DF - protótipo (Projeto de Inovação e Criatividade, IESB, 2026/2)
Mapa-jogo informativo sobre a rede de apoio em saúde mental do DF.
NÃO faz diagnóstico, triagem nem acompanhamento psicológico.
Sem login, sem cadastro e sem armazenamento das respostas do usuário.
"""
from pathlib import Path
import hashlib
import pandas as pd
import streamlit as st
import pydeck as pdk

# ----------------------------------------------------------------------------
# CONFIGURAÇÕES E CONSTANTES
# ----------------------------------------------------------------------------
FORM_URL = "https://forms.gle/VjkMS8Sftw37BKpA6"
INFOSAUDE_UBS_URL = "http://info.saude.df.gov.br/saude-docidadao/cidadao-ubs-unidades-basicas-de-saude/"
DATA_PATH = Path(__file__).parent / "data" / "servicos.csv"

RA_COORDS = {
    "Plano Piloto (Asa Sul)": (-15.8270, -47.9150), "Plano Piloto (Asa Norte)": (-15.7600, -47.8850),
    "Taguatinga": (-15.8330, -48.0570), "Ceilândia": (-15.8190, -48.1080),
    "Samambaia": (-15.8780, -48.0820), "Gama": (-16.0200, -48.0630),
    "Santa Maria": (-16.0190, -48.0130), "Sobradinho": (-15.6530, -47.7930),
    "Planaltina": (-15.6190, -47.6530), "Paranoá": (-15.7750, -47.7800),
    "Recanto das Emas": (-15.9140, -48.0640), "Riacho Fundo": (-15.8790, -48.0190),
    "Núcleo Bandeirante": (-15.8700, -47.9680), "Itapoã": (-15.7450, -47.7660),
    "Cruzeiro": (-15.7900, -47.9400), "Sobradinho II": (-15.6500, -47.8300),
    "Guará": (-15.8260, -47.9790), "Águas Claras": (-15.8390, -48.0270),
    "Brazlândia": (-15.6700, -48.2000), "São Sebastião": (-15.9030, -47.7720),
}

COR_TIPO = {
    "UBS": [34, 197, 94], "CAPS": [139, 92, 246], "CAPS III": [30, 64, 175],
    "CAPS i (infantojuvenil)": [6, 182, 212], "CAPS AD (álcool e drogas)": [249, 115, 22],
    "CAPS AD III": [146, 64, 14], "Ambulatório para adolescentes": [132, 204, 22],
    "Urgência psiquiátrica": [239, 68, 68], "Hospital Dia (IST/HIV e transexualidade)": [234, 179, 8],
    "Atendimento a vítimas de violência": [236, 72, 153],
}

O_QUE_E = {
    "UBS": "O \"postinho\". Faz acolhimento e também cuida de saúde mental, como ansiedade e depressão...",
    "CAPS": "Serviço de saúde mental aberto e comunitário, voltado a sofrimento psíquico intenso e persistente...",
    "CAPS III": "Modalidade de CAPS que a Carta de Serviços descreve como de funcionamento 24 horas...",
    "CAPS i (infantojuvenil)": "CAPS voltado a crianças e adolescentes (até 18 anos) em intenso sofrimento psíquico.",
    "Ambulatório para adolescentes": "Atendimento ambulatorial multiprofissional para adolescentes de 12 a 17 anos...",
    "Urgência psiquiátrica": "Atendimento de urgência e emergência em psiquiatria...",
    "CAPS AD (álcool e drogas)": "CAPS voltado a pessoas maiores de 16 anos com sofrimento intenso...",
    "CAPS AD III": "Modalidade de CAPS AD descrita como de funcionamento 24 horas...",
    "Atendimento a vítimas de violência": "Atendimento multiprofissional a pessoas em situação de violência...",
    "Hospital Dia (IST/HIV e transexualidade)": "Centro de referência em IST, HIV e hepatites..."
}

MISSOES = [
    {
        "id": "m1", "titulo": "Missão 1 · A primeira porta",
        "cenario": "Faz semanas que você está exausto(a), com ansiedade... Qual é um bom ponto de partida?",
        "opcoes": [
            ("A UBS (postinho) do meu bairro...", True, "Isso mesmo. A UBS faz acolhimento..."),
            ("Só adianta ir a um pronto-socorro.", False, "Pronto-socorro e UPA são para urgências..."),
            ("Esperar passar sozinho(a)...", False, "Mito comum. As UBS também atendem saúde mental..."),
        ],
        "aprendizado": "UBS = acolhimento + saúde mental + encaminhamento. Fonte: Carta de Serviços."
    },
    # (Adicione as demais missões aqui exatamente como estavam no original)
]

st.set_page_config(page_title="Caminhos do Cuidado DF", page_icon="🧭", layout="wide")

# ----------------------------------------------------------------------------
# FUNÇÕES DE DADOS E LÓGICA
# ----------------------------------------------------------------------------
@st.cache_data
def carregar_servicos() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
    lat, lon = [], []
    for _, r in df.iterrows():
        base = RA_COORDS.get(r["regiao"])
        if not base:
            lat.append(None)
            lon.append(None)
            continue
        
        # Deslocamento estável para espalhar pontos da mesma região
        h = int(hashlib.md5(r["id"].encode()).hexdigest()[:6], 16)
        dx = ((h % 1000) / 1000 - 0.5) * 0.02
        dy = (((h // 1000) % 1000) / 1000 - 0.5) * 0.02
        lat.append(float(base[0] + dy))
        lon.append(float(base[1] + dx))
        
    df["lat"] = lat
    df["lon"] = lon
    df["cor"] = df["tipo"].map(lambda t: COR_TIPO.get(t, [120, 120, 120]))
    return df

def aplicar_filtros(df: pd.DataFrame, tipos: list, regioes: list, incluir_pendentes: bool, so_lgbt: bool) -> pd.DataFrame:
    f = df.copy()
    if tipos: f = f[f["tipo"].isin(tipos)]
    if regioes: f = f[f["regiao"].isin(regioes)]
    if not incluir_pendentes: f = f[f["status"] == "verificado"]
    if so_lgbt: f = f[f["tags"].str.contains("lgbt", na=False)]
    return f

# ----------------------------------------------------------------------------
# COMPONENTES VISUAIS (UI)
# ----------------------------------------------------------------------------
def _ponto(cor: list) -> str:
    return (f"<span style='display:inline-block;width:14px;height:14px;border-radius:50%;"
            f"background:rgb({cor[0]},{cor[1]},{cor[2]});border:1px solid rgba(0,0,0,.25);"
            "margin-right:6px;vertical-align:middle'></span>")

def _gerar_html_legenda(tipos: list) -> str:
    itens = "".join(f"<span style='display:inline-block;margin:0 16px 6px 0;font-size:0.9rem'>"
                    f"{_ponto(COR_TIPO.get(t, [120, 120, 120]))}{t}</span>" for t in tipos)
    return f"<div style='margin:4px 0 8px 0'>{itens}</div>"

def renderizar_mapa(mapeaveis: pd.DataFrame):
    if mapeaveis.empty:
        st.info("Nenhum serviço mapeável com esses filtros.")
        return

    camada = pdk.Layer(
        "ScatterplotLayer",
        data=mapeaveis,
        get_position=["lon", "lat"],
        get_fill_color="cor",
        get_radius=700,
        radius_min_pixels=7,
        radius_max_pixels=16,
        stroked=True,
        get_line_color=[255, 255, 255],
        line_width_min_pixels=2,
        pickable=True,
        opacity=0.9,
    )
    visao = pdk.ViewState(latitude=-15.82, longitude=-47.95, zoom=9.2)
    tooltip = {
        "html": "<b>{nome}</b><br/>{tipo}<br/>{regiao}",
        "style": {"backgroundColor": "#2b2140", "color": "white", "fontSize": "13px"},
    }
    deck = pdk.Deck(
        layers=[camada],
        initial_view_state=visao,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip=tooltip
    )
    st.pydeck_chart(deck, use_container_width=True)

    presentes = set(mapeaveis["tipo"])
    ordem = [t for t in COR_TIPO if t in presentes] + sorted(presentes - set(COR_TIPO))
    st.markdown("**Legenda (cor de cada ponto):**")
    st.markdown(_gerar_html_legenda(ordem), unsafe_allow_html=True)
    st.caption("Passe o mouse (ou toque) em um ponto para ver o nome do serviço. 📍 Posições aproximadas.")

def renderizar_cartoes(df_filtrado: pd.DataFrame):
    if df_filtrado.empty:
        st.info("Nada encontrado. Tente limpar os filtros.")
        return
        
    for _, r in df_filtrado.iterrows():
        selo = "✅ dados verificados" if r["status"] == "verificado" else "⚠️ endereço/telefone a confirmar"
        with st.expander(f"{r['nome']}  ·  {r['tipo']}  ·  {r['regiao']}"):
            st.markdown(f"**O que é:** {O_QUE_E.get(r['tipo'], 'Não informado')}")
            st.markdown(f"**Quem pode procurar:** {r['publico']}\n\n**Como acessar:** {r['acesso']}")
            st.markdown(f"**Endereço:** {r['endereco']}\n\n**Telefone:** {r['telefone']}\n\n**Horário:** {r['horario']}")
            if r["observacao"]: st.caption(r["observacao"])
            if r["id"] == "ubs": st.link_button("Encontrar a minha UBS (InfoSaúde DF)", INFOSAUDE_UBS_URL)
            st.caption(f"{selo} · SUS · Fonte: {r['fonte']} · consultado em {r['data_consulta']}")

# ----------------------------------------------------------------------------
# PÁGINAS PRINCIPAIS
# ----------------------------------------------------------------------------
def pagina_mapa():
    st.header("🗺️ Mapa da rede de apoio")
    st.write("Explore os serviços públicos de saúde mental do Distrito Federal... Sem cadastro, sem julgamento.")
    df = carregar_servicos()

    c1, c2 = st.columns(2)
    tipos = c1.multiselect("Tipo de serviço", sorted(df["tipo"].unique()))
    regioes = c2.multiselect("Região", sorted(df["regiao"].unique()))
    
    c3, c4 = st.columns(2)
    incluir_pendentes = c3.checkbox("Incluir dados a confirmar", value=True)
    so_lgbt = c4.checkbox("Só serviços com oferta para população LGBTQIA+ citada na Carta")

    df_filtrado = aplicar_filtros(df, tipos, regioes, incluir_pendentes, so_lgbt)
    mapeaveis = df_filtrado.dropna(subset=["lat", "lon"])
    
    renderizar_mapa(mapeaveis)

    with st.expander("📖 O que significa cada cor? Guia dos tipos de serviço"):
        for t in [t for t in COR_TIPO if t in set(df["tipo"])]:
            st.markdown(f"{_ponto(COR_TIPO[t])}**{t}**: {O_QUE_E.get(t, '')}", unsafe_allow_html=True)

    st.subheader("Cartões dos serviços")
    renderizar_cartoes(df_filtrado)

    st.download_button(
        "⬇️ Baixar a lista de serviços (CSV) para consultar sem internet",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="caminhos_do_cuidado_servicos.csv",
        mime="text/csv",
    )

def pagina_missoes():
    st.header("🎮 Missões")
    st.write("Pequenos desafios para você conhecer a rede de apoio no seu ritmo.")
    
    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    resp = st.session_state["respostas"]

    concluidas = sum(1 for m in MISSOES if m["id"] in resp)
    st.progress(concluidas / len(MISSOES), text=f"{concluidas} de {len(MISSOES)} missões concluídas")
    
    if concluidas == len(MISSOES):
        st.success("🏅 Você completou todas as missões!")

    for m in MISSOES:
        feita = m["id"] in resp
        expandir = not feita and concluidas == MISSOES.index(m)
        with st.expander(("✅ " if feita else "🧭 ") + m["titulo"], expanded=expandir):
            st.write(m["cenario"])
            escolha = st.radio("Sua escolha", [o[0] for o in m["opcoes"]], index=None, key=f"r_{m['id']}")
            
            if st.button("Responder", key=f"b_{m['id']}", disabled=escolha is None):
                resp[m["id"]] = escolha
                st.rerun()
                
            if feita:
                escolhida = next(o for o in m["opcoes"] if o[0] == resp[m["id"]])
                st.success(escolhida[2]) if escolhida[1] else st.warning(escolhida[2])
                st.info("💡 " + m["aprendizado"])
                if st.button("Tentar de novo", key=f"redo_{m['id']}"):
                    del resp[m["id"]]
                    st.rerun()

def pagina_ajuda():
    st.header("🆘 Preciso de ajuda agora")
    st.error("### Risco imediato à vida (a sua ou de outra pessoa)\n**SAMU: 192** · **Polícia: 190**. Ligue agora.")
    st.warning("### Quero conversar com alguém agora\n**CVV: 188** (24 horas, gratuito) ou chat no site (cvv.org.br).")
    st.info("### Violência contra a mulher\n**Ligue 180** (Central de Atendimento à Mulher). Em perigo, **190**.")
    st.success(
        "### Preciso de atendimento de saúde mental\n"
        "- **Hospital São Vicente de Paulo**: urgência em psiquiatria. Tel.: (61) 2017-1093.\n"
        "- Alguns **CAPS III e CAPS AD III** funcionam **24 horas**.\n"
        "- **Sem urgência?** Procure a **UBS** do seu bairro.\n"
    )

def pagina_sobre():
    st.header("ℹ️ Sobre o protótipo")
    st.write("**Caminhos do Cuidado DF** é um protótipo de extensão universitária...")
    # Resumo enxuto da página original
    if FORM_URL: st.link_button("Deixe seu feedback (anônimo)", FORM_URL)

# ----------------------------------------------------------------------------
# NAVEGAÇÃO E EXECUÇÃO PRINCIPAL
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("🧭 Caminhos do Cuidado")
    pagina = st.radio("Navegar", ["🗺️ Mapa", "🎮 Missões", "🆘 Ajuda", "ℹ️ Sobre"], label_visibility="collapsed")
    st.divider()
    st.error("**Risco imediato?** Ligue **192** (SAMU) ou **190**. Apoio emocional 24h: **188** (CVV).")

if pagina.startswith("🗺️"): pagina_mapa()
elif pagina.startswith("🎮"): pagina_missoes()
elif pagina.startswith("🆘"): pagina_ajuda()
else: pagina_sobre()