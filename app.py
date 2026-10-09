"""
Caminhos do Cuidado DF - protótipo (Projeto de Inovação e Criatividade, IESB, 2026/2)

Mapa-jogo informativo sobre a rede de apoio em saúde mental do DF.
NÃO faz diagnóstico, triagem nem acompanhamento psicológico.
Sem login, sem cadastro e sem armazenamento das respostas do usuário.

Rodar localmente:  streamlit run app.py
"""
from pathlib import Path
import hashlib

import pandas as pd
import streamlit as st

try:
    import pydeck as pdk
except Exception:  # pydeck normalmente já vem com o Streamlit
    pdk = None

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO (edite aqui)
# ----------------------------------------------------------------------------
FORM_URL = ""  # cole o link do Google Forms de feedback anônimo (validação)
INFOSAUDE_UBS_URL = "http://info.saude.df.gov.br/saude-docidadao/cidadao-ubs-unidades-basicas-de-saude/"
DATA_PATH = Path(__file__).parent / "data" / "servicos.csv"

st.set_page_config(page_title="Caminhos do Cuidado DF", page_icon="🧭", layout="wide")

# Centros APROXIMADOS das Regiões Administrativas (só para posicionar os pontos).
RA_COORDS = {
    "Plano Piloto (Asa Sul)": (-15.8270, -47.9150),
    "Plano Piloto (Asa Norte)": (-15.7600, -47.8850),
    "Taguatinga": (-15.8330, -48.0570),
    "Ceilândia": (-15.8190, -48.1080),
    "Samambaia": (-15.8780, -48.0820),
    "Gama": (-16.0200, -48.0630),
    "Santa Maria": (-16.0190, -48.0130),
    "Sobradinho": (-15.6530, -47.7930),
    "Planaltina": (-15.6190, -47.6530),
    "Paranoá": (-15.7750, -47.7800),
    "Recanto das Emas": (-15.9140, -48.0640),
    "Riacho Fundo": (-15.8790, -48.0190),
    "Núcleo Bandeirante": (-15.8700, -47.9680),
    "Itapoã": (-15.7450, -47.7660),
    "Guará": (-15.8260, -47.9790),
    "Águas Claras": (-15.8390, -48.0270),
    "Brazlândia": (-15.6700, -48.2000),
    "São Sebastião": (-15.9030, -47.7720),
}

COR_TIPO = {
    "UBS": [52, 211, 153],
    "CAPS": [139, 92, 246],
    "CAPS III (24h)": [109, 40, 217],
    "CAPS i (infantojuvenil)": [168, 85, 247],
    "Ambulatório para adolescentes": [96, 165, 250],
    "Urgência psiquiátrica": [244, 63, 94],
    "Hospital Dia (IST/HIV e transexualidade)": [251, 191, 36],
    "CAPS AD (álcool e drogas)": [99, 102, 241],
    "CAPS AD III (24h)": [67, 56, 202],
    "Atendimento a vítimas de violência": [236, 72, 153],
}

# Explicações em linguagem simples (baseadas na Carta de Serviços da SES-DF).
O_QUE_E = {
    "UBS": (
        "O \"postinho\". Faz acolhimento e também cuida de saúde mental, como ansiedade e depressão, "
        "além de consultas, vacinas e outros serviços. O acolhimento é garantido a qualquer cidadão "
        "e a equipe pode encaminhar para outros serviços da rede."
    ),
    "CAPS": (
        "Serviço de saúde mental aberto e comunitário, voltado a sofrimento psíquico intenso e persistente, "
        "incluindo necessidades ligadas a álcool e outras drogas. Recebe quem chega por conta própria "
        "ou encaminhado. O ideal é procurar o CAPS da sua região."
    ),
    "CAPS III (24h)": (
        "CAPS que funciona 24 horas, inclusive feriados e fins de semana, com acolhimento noturno. "
        "Atende maiores de 18 anos em intenso sofrimento psíquico."
    ),
    "CAPS i (infantojuvenil)": (
        "CAPS voltado a crianças e adolescentes (até 18 anos) em intenso sofrimento psíquico."
    ),
    "Ambulatório para adolescentes": (
        "Atendimento ambulatorial multiprofissional para adolescentes de 12 a 17 anos, "
        "com acesso por encaminhamento da UBS."
    ),
    "Urgência psiquiátrica": (
        "Atendimento de urgência e emergência em psiquiatria, para quando o cuidado não pode esperar."
    ),
    "CAPS AD (álcool e drogas)": (
        "CAPS voltado a pessoas maiores de 16 anos com sofrimento intenso decorrente do uso prejudicial "
        "de álcool e outras drogas. Aceita procura direta ou encaminhamento."
    ),
    "CAPS AD III (24h)": (
        "CAPS AD que funciona 24 horas, com acolhimento noturno, para pessoas maiores de 16 anos "
        "com sofrimento intenso ligado ao uso de álcool e outras drogas."
    ),
    "Atendimento a vítimas de violência": (
        "Atendimento multiprofissional a pessoas em situação de violência. Para mulheres, atendimento "
        "psicológico e social; para crianças e adolescentes, psicológico, médico e social, conforme o "
        "documento da Região de Saúde Oeste."
    ),
    "Hospital Dia (IST/HIV e transexualidade)": (
        "Centro de referência em IST, HIV e hepatites, que também oferece ambulatório de transexualidade e PrEP, "
        "segundo a Carta de Serviços. Não é um serviço de saúde mental, mas faz parte da rede de saúde do DF."
    ),
}

# ----------------------------------------------------------------------------
# DADOS
# ----------------------------------------------------------------------------
@st.cache_data
def carregar_servicos() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
    lat, lon = [], []
    for _, r in df.iterrows():
        base = RA_COORDS.get(r["regiao"])
        if base is None:
            lat.append(None)
            lon.append(None)
            continue
        # deslocamento pequeno e estável, para pontos da mesma região não ficarem empilhados
        h = int(hashlib.md5(r["id"].encode()).hexdigest()[:6], 16)
        dx = ((h % 1000) / 1000 - 0.5) * 0.02
        dy = (((h // 1000) % 1000) / 1000 - 0.5) * 0.02
        lat.append(base[0] + dy)
        lon.append(base[1] + dx)
    df["lat"] = lat
    df["lon"] = lon
    df["cor"] = df["tipo"].map(lambda t: COR_TIPO.get(t, [120, 120, 120]))
    return df


# ----------------------------------------------------------------------------
# BARRA LATERAL
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("🧭 Caminhos do Cuidado DF")
    pagina = st.radio(
        "Navegar",
        ["🗺️ Mapa de apoio", "🎮 Missões", "🆘 Preciso de ajuda agora", "ℹ️ Sobre o protótipo"],
        label_visibility="collapsed",
    )
    st.divider()
    st.error("**Risco imediato?** Ligue **192** (SAMU) ou **190**. Apoio emocional 24h: **188** (CVV).")
    st.caption("Sem login. Nada do que você responde aqui é guardado.")


# ----------------------------------------------------------------------------
# PÁGINA: MAPA
# ----------------------------------------------------------------------------
def pagina_mapa():
    st.header("🗺️ Mapa da rede de apoio")
    st.write(
        "Explore os serviços públicos de saúde mental do Distrito Federal, entenda **o que cada um faz** "
        "e **como chegar lá**. Sem cadastro, sem julgamento."
    )
    df = carregar_servicos()

    c1, c2 = st.columns(2)
    tipos = c1.multiselect("Tipo de serviço", sorted(df["tipo"].unique()))
    regioes = c2.multiselect("Região", sorted(df["regiao"].unique()))
    c3, c4 = st.columns(2)
    incluir_pendentes = c3.checkbox("Incluir dados a confirmar", value=True)
    so_lgbt = c4.checkbox(
        "Só serviços com oferta para população LGBTQIA+ citada na Carta",
        help="Baseado no que a Carta de Serviços da SES-DF descreve. Não mede a qualidade do acolhimento.",
    )

    f = df.copy()
    if tipos:
        f = f[f["tipo"].isin(tipos)]
    if regioes:
        f = f[f["regiao"].isin(regioes)]
    if not incluir_pendentes:
        f = f[f["status"] == "verificado"]
    if so_lgbt:
        f = f[f["tags"].str.contains("lgbt")]

    mapeaveis = f.dropna(subset=["lat", "lon"])
    if not mapeaveis.empty:
        if pdk is not None:
            camada = pdk.Layer(
                "ScatterplotLayer",
                data=mapeaveis[["nome", "tipo", "regiao", "lat", "lon", "cor"]],
                get_position="[lon, lat]",
                get_fill_color="cor",
                get_radius=900,
                pickable=True,
                opacity=0.85,
            )
            visao = pdk.ViewState(latitude=-15.82, longitude=-47.95, zoom=9.2)
            st.pydeck_chart(
                pdk.Deck(
                    layers=[camada],
                    initial_view_state=visao,
                    map_style="light",
                    tooltip={"text": "{nome}\n{tipo}\n{regiao}"},
                )
            )
        else:
            st.map(mapeaveis, latitude="lat", longitude="lon")
        st.caption("📍 Posições **aproximadas** (centro da região administrativa). Use o endereço do cartão abaixo.")
    else:
        st.info("Nenhum serviço mapeável com esses filtros.")

    st.subheader("Cartões dos serviços")
    if f.empty:
        st.info("Nada encontrado. Tente limpar os filtros.")
        return
    for _, r in f.iterrows():
        selo = "✅ dados verificados" if r["status"] == "verificado" else "⚠️ endereço/telefone a confirmar"
        selo += " · 🏥 serviço público (SUS)"
        with st.expander(f"{r['nome']}  ·  {r['tipo']}  ·  {r['regiao']}"):
            st.markdown(f"**O que é:** {O_QUE_E.get(r['tipo'], '')}")
            st.markdown(f"**Quem pode procurar:** {r['publico']}")
            st.markdown(f"**Como acessar:** {r['acesso']}")
            st.markdown(f"**Endereço:** {r['endereco']}")
            st.markdown(f"**Telefone:** {r['telefone']}")
            st.markdown(f"**Horário:** {r['horario']}")
            if r["observacao"]:
                st.caption(r["observacao"])
            if r["id"] == "ubs":
                st.link_button("Encontrar a minha UBS (InfoSaúde DF)", INFOSAUDE_UBS_URL)
            st.caption(f"{selo} · Fonte: {r['fonte']} · consultado em {r['data_consulta']}")

    colunas_csv = ["nome", "tipo", "regiao", "endereco", "telefone", "horario", "acesso", "publico",
                   "fonte", "data_consulta", "status"]
    st.download_button(
        "⬇️ Baixar a lista de serviços (CSV) para consultar sem internet",
        data=df[colunas_csv].to_csv(index=False).encode("utf-8-sig"),
        file_name="caminhos_do_cuidado_servicos.csv",
        mime="text/csv",
    )


# ----------------------------------------------------------------------------
# PÁGINA: MISSÕES
# ----------------------------------------------------------------------------
MISSOES = [
    {
        "id": "m1",
        "titulo": "Missão 1 · A primeira porta",
        "cenario": (
            "Faz semanas que você está exausto(a), com ansiedade e sem conseguir se concentrar. "
            "Você quer conversar com alguém da saúde pública, mas não sabe por onde começar. "
            "Qual é um bom ponto de partida?"
        ),
        "opcoes": [
            ("A UBS (postinho) do meu bairro: o acolhimento é garantido e eles cuidam de ansiedade e depressão.", True,
             "Isso mesmo. A UBS faz acolhimento, atende saúde mental e pode encaminhar para outros serviços."),
            ("Só adianta ir a um pronto-socorro.", False,
             "Pronto-socorro e UPA são para urgências e emergências. Para o que não é urgente, a UBS é a porta de entrada."),
            ("Esperar passar sozinho(a); postinho é só para vacina.", False,
             "Mito comum. As UBS também atendem saúde mental, como ansiedade e depressão, e o acolhimento é garantido."),
        ],
        "aprendizado": "UBS = acolhimento + saúde mental + encaminhamento. Fonte: Carta de Serviços da SES-DF.",
    },
    {
        "id": "m2",
        "titulo": "Missão 2 · Mito ou fato: CAPS",
        "cenario": "Um colega diz: \"CAPS é só para quem perdeu a cabeça.\" Qual afirmação é a mais correta?",
        "opcoes": [
            ("CAPS é serviço aberto e comunitário, para sofrimento psíquico intenso e persistente, e recebe quem chega por conta própria ou encaminhado.", True,
             "Correto. O CAPS é um serviço de saúde, aberto e comunitário, e a procura direta é aceita."),
            ("CAPS só atende com internação.", False,
             "Não. O cuidado é feito em atividades como consultas, grupos e oficinas. A internação não é o centro do serviço."),
            ("CAPS é um serviço privado e pago.", False,
             "Não. Os CAPS fazem parte da rede pública (SUS) do DF."),
        ],
        "aprendizado": "CAPS atende demanda espontânea ou encaminhada; o ideal é procurar o da sua região. Fonte: Carta de Serviços da SES-DF.",
    },
    {
        "id": "m3",
        "titulo": "Missão 3 · O que levar?",
        "cenario": "Você decidiu ir a uma UBS ou a um CAPS. O que é recomendado levar?",
        "opcoes": [
            ("Documento oficial com foto e Cartão SUS (comprovante de residência é recomendado, mas não obrigatório).", True,
             "Isso. E pessoas em situação de rua não precisam apresentar esses documentos."),
            ("Um laudo médico, sem ele não me atendem.", False,
             "Não é preciso laudo para ser acolhido. O acolhimento é o primeiro passo."),
            ("Nada, nem documento.", False,
             "Leve o documento com foto e o Cartão SUS, porque facilitam o cadastro. Quem está em situação de rua é exceção."),
        ],
        "aprendizado": "Documento com foto + Cartão SUS. Comprovante de residência: recomendado, não obrigatório. Fonte: Carta de Serviços da SES-DF.",
    },
    {
        "id": "m4",
        "titulo": "Missão 4 · Quando um amigo está em crise",
        "cenario": (
            "Um amigo te diz que não aguenta mais e fala em se machucar. Ele pede que você \"não conte pra ninguém\". "
            "O que ajuda mais agora?"
        ),
        "opcoes": [
            ("Ficar com ele, ouvir sem julgar, não deixá-lo sozinho e acionar ajuda: SAMU 192 se houver risco imediato, e o CVV (188) está disponível 24h.", True,
             "Isso. Você não precisa resolver sozinho(a). Segurança vem primeiro, e pedir ajuda profissional é um ato de cuidado."),
            ("Guardar segredo e torcer para passar.", False,
             "Em situação de risco, guardar segredo pode deixar a pessoa ainda mais exposta. Acione ajuda."),
            ("Mandar ele conversar com uma IA e ficar tranquilo.", False,
             "Uma IA não substitui uma pessoa ao lado nem o atendimento de urgência."),
        ],
        "aprendizado": "Risco imediato: 192 (SAMU) ou 190. Apoio emocional 24h: 188 (CVV). CAPS III funciona 24h.",
    },
    {
        "id": "m5",
        "titulo": "Missão 5 · IA e redes: apoio com limites",
        "cenario": (
            "Muita gente desabafa com IAs e nas redes porque é rápido e sem julgamento. "
            "Qual atitude ajuda mais?"
        ),
        "opcoes": [
            ("Usar como apoio para organizar os pensamentos, mas procurar uma pessoa/serviço de saúde se o mal-estar persistir.", True,
             "Isso. Ferramentas digitais podem ajudar a pôr as ideias em ordem, mas não substituem diagnóstico nem cuidado humano."),
            ("Confiar na IA para dizer o que eu tenho e o que tomar.", False,
             "Diagnóstico e medicação são com profissionais de saúde. Uma IA pode errar e não conhece a sua situação."),
            ("Evitar qualquer ajuda, de qualquer tipo.", False,
             "Isolar-se tende a piorar. Existem serviços gratuitos prontos para acolher."),
        ],
        "aprendizado": "Tecnologia pode ser a ponte; o cuidado é humano. Este app existe para levar você até os serviços reais.",
    },
    {
        "id": "m6",
        "titulo": "Missão 6 · Rede de proteção à mulher",
        "cenario": "Uma colega sofre violência em casa e não sabe a quem recorrer. Que canal você indica?",
        "opcoes": [
            ("Ligue 180 (Central de Atendimento à Mulher), e 190 em caso de perigo imediato.", True,
             "Isso. O Ligue 180 é um canal nacional de orientação e denúncia; em perigo imediato, o 190."),
            ("Dizer que isso é problema de casal e não se intrometer.", False,
             "Violência não é assunto privado. Indicar um canal de ajuda pode salvar vidas."),
            ("Procurar só pelas redes sociais.", False,
             "Redes não garantem acolhimento nem proteção. Prefira os canais oficiais."),
        ],
        "aprendizado": "Ligue 180 (orientação e denúncia) e 190 (emergência). Conecta o projeto ao ODS 5.",
    },
]


def pagina_missoes():
    st.header("🎮 Missões")
    st.write("Pequenos desafios para você conhecer a rede de apoio **no seu ritmo**. Não é prova: errar faz parte.")
    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    resp = st.session_state["respostas"]

    concluidas = sum(1 for m in MISSOES if m["id"] in resp)
    st.progress(concluidas / len(MISSOES), text=f"{concluidas} de {len(MISSOES)} missões concluídas")
    if concluidas == len(MISSOES):
        st.success("🏅 Você completou todas as missões! Agora você conhece melhor os caminhos do cuidado.")

    for m in MISSOES:
        feita = m["id"] in resp
        with st.expander(("✅ " if feita else "🧭 ") + m["titulo"], expanded=not feita and concluidas == MISSOES.index(m)):
            st.write(m["cenario"])
            textos = [o[0] for o in m["opcoes"]]
            escolha = st.radio("Sua escolha", textos, index=None, key=f"radio_{m['id']}")
            if st.button("Responder", key=f"btn_{m['id']}", disabled=escolha is None):
                resp[m["id"]] = escolha
                st.rerun()
            if feita:
                escolhida = next(o for o in m["opcoes"] if o[0] == resp[m["id"]])
                if escolhida[1]:
                    st.success(escolhida[2])
                else:
                    st.warning(escolhida[2])
                st.info("💡 " + m["aprendizado"])
                if st.button("Tentar de novo", key=f"redo_{m['id']}"):
                    del resp[m["id"]]
                    st.rerun()

    st.caption("As suas respostas ficam apenas nesta sessão do navegador e somem ao fechar a página.")


# ----------------------------------------------------------------------------
# PÁGINA: AJUDA AGORA
# ----------------------------------------------------------------------------
def pagina_ajuda():
    st.header("🆘 Preciso de ajuda agora")
    st.write("Você não está sozinho(a). Escolha o que mais se parece com o seu momento.")

    st.error("### Risco imediato à vida (a sua ou de outra pessoa)\n**SAMU: 192** · **Polícia: 190**. Ligue agora.")
    st.warning(
        "### Quero conversar com alguém agora\n"
        "**CVV: 188** (24 horas, gratuito). Há também chat no site do CVV (cvv.org.br)."
    )
    st.info(
        "### Violência contra a mulher\n"
        "**Ligue 180** (Central de Atendimento à Mulher). Em perigo imediato, **190**."
    )
    st.success(
        "### Preciso de atendimento de saúde mental\n"
        "- **Hospital São Vicente de Paulo** (Taguatinga Sul): urgência em psiquiatria. Tel.: (61) 2017-1093.\n"
        "- **CAPS III e CAPS AD III** funcionam **24 horas**, procure o da sua região.\n"
        "- **Sem urgência?** Procure a **UBS** do seu bairro, onde o acolhimento é garantido.\n"
    )
    st.caption(
        "Fontes: Carta de Serviços da SES-DF; números nacionais 192, 190, 188 e 180. "
        "Confirme sempre telefones e horários antes de ir."
    )


# ----------------------------------------------------------------------------
# PÁGINA: SOBRE
# ----------------------------------------------------------------------------
def pagina_sobre():
    st.header("ℹ️ Sobre o protótipo")
    st.write(
        "**Caminhos do Cuidado DF** é um protótipo de extensão universitária (Projeto de Inovação e Criatividade, "
        "IESB, 2026/2). A ideia é ser uma **ponte** entre jovens e a rede pública de saúde mental que já existe no DF."
    )
    st.subheader("O que este app NÃO faz")
    st.markdown(
        "- Não faz diagnóstico, triagem nem acompanhamento psicológico.\n"
        "- Não substitui profissionais de saúde nem serviços de urgência.\n"
        "- Não pede cadastro e não guarda as suas respostas."
    )
    st.subheader("O que este protótipo já tem")
    st.markdown(
        "- Mapa e cartões com serviços e explicações em linguagem simples.\n"
        "- Missões educativas sobre acesso, mitos e rede de proteção.\n"
        "- Página de ajuda imediata.\n"
        "- Download da lista de serviços (CSV) para consultar sem internet (versão simples do modo offline).\n"
        "- Filtro por oferta para população LGBTQIA+ **citada na Carta de Serviços da SES-DF**."
    )
    st.subheader("Ainda não implementado (trabalho futuro)")
    st.markdown(
        "- Tempo de espera: não encontramos dado público por serviço; só seria possível com coleta real.\n"
        "- Avaliações anônimas de estudantes: exigem coleta real e moderação, por se tratar de saúde mental.\n"
        "- Avaliação do acolhimento (por exemplo, serviços amigáveis à população LGBTQIA+): exige relatos reais.\n"
        "- Modo offline completo (aplicativo instalável).\n"
        "- Lista completa de CAPS e UBS com endereços verificados."
    )
    df = carregar_servicos()
    st.subheader("Dados e fontes")
    st.write(
        f"Serviços cadastrados: **{len(df)}** · com dados verificados: **{(df['status'] == 'verificado').sum()}** · "
        f"última consulta: **{df['data_consulta'].max()}**."
    )
    st.caption("Fonte principal: Carta de Serviços ao Cidadão da SES-DF. Posições no mapa são aproximadas.")
    st.subheader("Deixe seu feedback (anônimo)")
    if FORM_URL:
        st.link_button("Responder o formulário", FORM_URL)
    else:
        st.info("Configure FORM_URL em app.py com o link do Google Forms de feedback.")


if pagina.startswith("🗺️"):
    pagina_mapa()
elif pagina.startswith("🎮"):
    pagina_missoes()
elif pagina.startswith("🆘"):
    pagina_ajuda()
else:
    pagina_sobre()
