import os
import warnings

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

warnings.filterwarnings('ignore')

# =========================================================
# CONFIG
# =========================================================

path_main = os.getcwd()
name_file = "Exemplo.xlsx"
title = "Dashboard " + name_file.replace(".xlsx", "").replace("_", " ")

st.set_page_config(
    page_title=title,
    page_icon="📊",
    layout="wide"
)

st.title(f"📊 {title}")

st.markdown("""
<style>

/* FUNDO */
.stApp {
    background-color: #d9d9db;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #001d3d;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* TÍTULOS */
h1, h2, h3 {
    color: #222 !important;
    text-align: center !important;
    font-weight: 700 !important;
}

h1 {
    margin-top: 2rem !important;
}

/* CARDS */
.gray-card {
    background: #ececec;
    padding: 18px;
    border-radius: 24px;
    box-shadow:
        0 4px 15px rgba(0,0,0,0.12);
    margin-bottom: 15px;
}

/* TABELAS */
.table-card {
    background: #ececec;
    padding: 16px;
    border-radius: 24px;
    box-shadow:
        0 4px 15px rgba(0,0,0,0.12);
}

/* SELECTBOX */
div[data-baseweb="select"] > div {
    background-color: #f2f2f2 !important;
    border-radius: 12px !important;
    border: 1px solid #d0d0d0 !important;
}

/* MULTISELECT */
[data-baseweb="tag"] {
    background-color: #001d3d !important;
}

/* LABELS */
label {
    font-weight: 700 !important;
    color: white !important;
}


[data-testid="stSidebar"] h1 {
    color: #ffffff !important;
}

/* CONTAINER PRINCIPAL */
div.block-container {
    padding-top: 1rem;
}

/* Scroll para gráficos */
.scroll-chart {
    height: 500px;
    overflow-y: auto;
    overflow-x: hidden;
    border: 1px solid #DDD;
    border-radius: 10px;
    padding: 10px;
    background-color: white;
}

/* SCROLL */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #a8a8a8;
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)

CARD_BG = "#F7F8FA"

st.markdown(f"""
<style>

/* FUNDO GERAL */
.stApp {{
    background-color: #EDEDED;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background-color: #001D3D;
}}

/* CARDS */
.gray-card {{
    background: {CARD_BG};
    border-radius: 26px;
    padding: 20px;
    box-shadow:
        0 4px 15px rgba(0,0,0,0.10);
    margin-bottom: 15px;
}}

/* DATAFRAME */
[data-testid="stDataFrame"] {{
    border-radius: 18px;
    overflow: hidden;
}}

/* SELECTBOX */
div[data-baseweb="select"] > div {{
    background-color: #F7F8FA !important;
    border-radius: 14px !important;
    border: 1px solid #D8D8D8 !important;
}}


div[data-testid="stFullScreenFrame"] {{
    border: 1px solid #D8D8D8 !important;
    padding: .5px !important;
    background-color: {CARD_BG} !important;
    border-radius: 1rem !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 102% !important;
    overflow: scroll !important;

}}

/* PAGER LABELS */
.pager-label {{
    color: #222222 !important;
    font-weight: 700;
    margin-bottom: 0.25rem;
}}

/* SCROLL */
::-webkit-scrollbar {{
    width: 8px;
}}

::-webkit-scrollbar-thumb {{
    background: #B8B8B8;
    border-radius: 20px;
}}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def carregar_dados():

    df = pd.read_excel(
        os.path.join(path_main, name_file)
    )

    df["Data"] = pd.to_datetime(
        df["Data"],
        format='%d/%m/%Y',
        errors='coerce'
    )

    df["Ano"] = df["Data"].dt.year.astype(str)
    df["Mês"] = df["Data"].dt.month.astype(str).str.zfill(2)

    df_group = (
        df.groupby(["Ano", "Mês", "Loja"], as_index=False)
        [["Nota Atingida", "Nota Possível"]]
        .sum()
    )

    df_group["Média"] = (
        df_group["Nota Atingida"] /
        df_group["Nota Possível"]
    )

    df_group["Ano / Mês"] = (
        df_group["Mês"] + "/" + df_group["Ano"]
    )

    df_group["Color"] = df_group["Média"].apply(
        lambda x: "#ff4b4b" if x < 0.88 else "#22c55e"
    )

    df_group = df_group.sort_values(
        by=["Ano", "Mês"]
    )

    return df, df_group

with st.spinner("Carregando dados... aguarde alguns segundos."):
    df, df_group = carregar_dados()

# =========================================================
# FILTROS
# =========================================================
st.sidebar.title("Filtros", )

list_meses = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez"
]

def aplicar_filtros(base_df, filtros, ignorar=None):
    df_tmp = base_df.copy()
    ignorar = ignorar or set()

    if "Ano" not in ignorar and filtros.get("Ano"):
        df_tmp = df_tmp[df_tmp["Ano"].isin(filtros["Ano"])]

    if "Mês" not in ignorar and filtros.get("Mês"):
        df_tmp = df_tmp[df_tmp["Mês"].isin(filtros["Mês"])]

    if "Loja" not in ignorar and filtros.get("Loja"):
        df_tmp = df_tmp[df_tmp["Loja"].isin(filtros["Loja"])]

    if "Tópico" not in ignorar and filtros.get("Tópico"):
        df_tmp = df_tmp[df_tmp["Tópico"].isin(filtros["Tópico"])]

    if "Tag" not in ignorar and filtros.get("Tag"):
        df_tmp = df_tmp[df_tmp["Tag"].isin(filtros["Tag"])]

    return df_tmp


def mes_num_para_nome(mes_num):
    return list_meses[int(mes_num) - 1]


def mes_nome_para_num(mes_nome):
    return str(list_meses.index(mes_nome) + 1).zfill(2)


filtros_atuais = {
    "Ano": st.session_state.get("filtro_ano", []),
    "Mês": st.session_state.get("filtro_mes", []),
    "Loja": st.session_state.get("filtro_loja", []),
    "Tópico": st.session_state.get("filtro_topico", []),
    "Tag": st.session_state.get("filtro_tag", []),
}

anos = sorted(
    aplicar_filtros(df, filtros_atuais, {"Ano"})["Ano"]
    .dropna()
    .unique()
)
filtros_atuais["Ano"] = [ano for ano in filtros_atuais["Ano"] if ano in anos]
st.session_state["filtro_ano"] = filtros_atuais["Ano"]

meses_base = aplicar_filtros(df, filtros_atuais, {"Mês"})["Mês"].dropna().unique()
meses = sorted(
    [mes_num_para_nome(mes) for mes in meses_base],
    key=lambda x: list_meses.index(x)
)
mes_nums_disponiveis = {mes_nome_para_num(mes) for mes in meses}
filtros_atuais["Mês"] = [mes for mes in filtros_atuais["Mês"] if mes in mes_nums_disponiveis]
st.session_state["filtro_mes"] = filtros_atuais["Mês"]

lojas = sorted(
    aplicar_filtros(df, filtros_atuais, {"Loja"})["Loja"]
    .dropna()
    .unique()
)
filtros_atuais["Loja"] = [loja for loja in filtros_atuais["Loja"] if loja in lojas]
st.session_state["filtro_loja"] = filtros_atuais["Loja"]

topicos = sorted(
    aplicar_filtros(df, filtros_atuais, {"Tópico"})["Tópico"]
    .dropna()
    .unique()
)
filtros_atuais["Tópico"] = [topico for topico in filtros_atuais["Tópico"] if topico in topicos]
st.session_state["filtro_topico"] = filtros_atuais["Tópico"]

tags = sorted(
    aplicar_filtros(df, filtros_atuais, {"Tag"})["Tag"]
    .dropna()
    .unique()
)
filtros_atuais["Tag"] = [tag for tag in filtros_atuais["Tag"] if tag in tags]
st.session_state["filtro_tag"] = filtros_atuais["Tag"]

ano_sel = st.sidebar.multiselect(
    "Ano",
    anos,
    key="filtro_ano"
)

mes_sel_nomes = st.sidebar.multiselect(
    "Mês",
    meses,
    default=[mes_num_para_nome(mes) for mes in filtros_atuais["Mês"]],
    key="filtro_mes_nomes"
)
mes_sel = [mes_nome_para_num(mes) for mes in mes_sel_nomes]
st.session_state["filtro_mes"] = mes_sel

loja_sel = st.sidebar.multiselect(
    "Loja",
    lojas,
    key="filtro_loja"
)

topico_sel = st.sidebar.multiselect(
    "Tópico",
    topicos,
    key="filtro_topico"
)

tag_sel = st.sidebar.multiselect(
    "Tag",
    tags,
    key="filtro_tag"
)

# =========================================================
# LAYOUT
# =========================================================

col1, col2 = st.columns(2, gap="medium")

# =========================================================
# Dados filtrados
# =========================================================

df_filtrado = df.copy()

if ano_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Ano"].isin(ano_sel)
    ]

if mes_sel:
    # Converter nomes de meses de volta para números
    mes_nums = [str(list_meses.index(m) + 1).zfill(2) for m in mes_sel]
    df_filtrado = df_filtrado[
        df_filtrado["Mês"].isin(mes_nums)
    ]

if loja_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Loja"].isin(loja_sel)
    ]

if topico_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Tópico"].isin(topico_sel)
    ]

if tag_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Tag"].isin(tag_sel)
    ]


media_geral = (
    df_filtrado["Nota Atingida"].sum() /
    df_filtrado["Nota Possível"].sum()
)

# =========================================================
# GRÁFICO 1
# =========================================================

# ======================================================
# VELOCÍMETRO
# ======================================================

with col1:

    st.subheader("Média / Meta")

    if media_geral >= 0.85:
        gauge_color = "#22C55E"
    elif media_geral >= 0.70:
        gauge_color = "#FDBA3B"
    else:
        gauge_color = "#FF4B4B"

    fig_gauge = go.Figure(go.Indicator(

        mode="gauge+number",

        value=media_geral * 100,

        number={
            'suffix': "%",
            'font': {
                'size': 48,
                'color': '#222'
            }
        },

        gauge={

            'axis': {
                'range': [0, 100],
                'tickwidth': 0
            },

            'bar': {
                'color': gauge_color,
                'thickness': 1.0
            },

            'bgcolor': "white",

            'steps': [
                {
                    'range': [0, 100],
                    'color': "#E5E7EB"
                }
            ],

            'threshold': {
                'line': {
                    'color': "#222",
                    'width': 10
                },
                'thickness': 0.8,
                'value': 85
            }
        }
    ))

    fig_gauge.update_layout(

        height=320,

        margin=dict(t=40, b=20, l=30, r=30),

        paper_bgcolor=CARD_BG,

        font={
            'color': "#222"
        }
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# GRÁFICO 2
# =========================================================
with col2:

    st.subheader("Média por Ano e Mês")

    df_mes = (
        df_filtrado
        .groupby(["Ano", "Mês"], as_index=False)
        .agg({
            "Nota Atingida": "sum",
            "Nota Possível": "sum"
        })
    )

    df_mes["Média"] = (
        df_mes["Nota Atingida"] /
        df_mes["Nota Possível"]
    )

    df_mes["AnoMes"] = (
        df_mes["Mês"] + "/" + df_mes["Ano"]
    )

    show_labels = len(df_mes) <= 14
    text_values = None
    if show_labels:
        text_values = [
            f"{v:.1%}".replace(".", ",")
            for v in df_mes["Média"]
        ]

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(

        x=df_mes["AnoMes"],
        y=df_mes["Média"],

        mode='lines+markers+text' if show_labels else 'lines+markers',

        text=text_values,

        textposition="top center",

        line=dict(
            color="#A8A8A8",
            width=4
        ),

        marker=dict(

            size=10,

            color=[
                "#22C55E" if v >= 0.85
                else "#FDBA3B" if v >= 0.70
                else "#FF4B4B"
                for v in df_mes["Média"]
            ]
        )
    ))

    fig_line.update_layout(

        height=320,

        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),

        xaxis=dict(
            showgrid=False,
            color="#666"
        ),

        yaxis=dict(
            tickformat=".0%",
            showgrid=False,
            color="#666"
        ),

        font=dict(
            color="#222"
        ),

        showlegend=False
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# # =========================================================
# # GRÁFICO 2 COM SCROLL
# # =========================================================
# with col2:

#     st.subheader("Ranking de Lojas")

#     # FULLSCREEN NATIVO STREAMLIT
#     chart_container = st.container(border=False)

#     df_rank = (
#         df_group
#         .groupby("Loja", as_index=False)
#         .agg({"Média": "mean"})
#         .sort_values(by="Média")
#     )

#     df_rank["Color"] = df_rank["Média"].apply(
#         lambda x: "#ff4b4b" if x < 0.88 else "#22c55e"
#     )

#     altura_grafico = max(len(df_rank) * 45, 400)

#     fig2 = go.Figure()

#     fig2.add_trace(go.Bar(
#         x=df_rank["Média"],
#         y=df_rank["Loja"],
#         orientation='h',

#         marker=dict(
#             color=df_rank["Color"]
#         ),

#         text=[
#             f"{v:.1%}".replace(".", ",")
#             for v in df_rank["Média"]
#         ],

#         # LABEL DENTRO DA BARRA
#         textposition='inside',

#         insidetextanchor='end',

#         textfont=dict(
#             size=13,
#             color="white"
#         )
#     ))

#     fig2.update_layout(

#         height=altura_grafico,

#         margin=dict(
#             l=260,   # espaço para nomes
#             r=40,
#             t=30,
#             b=30
#         ),

#         showlegend=False,

#         paper_bgcolor='#0E1117',
#         plot_bgcolor='#0E1117',

#         bargap=0.35,

#         font=dict(
#             color='white',
#             size=13
#         ),

#         xaxis=dict(
#             tickformat=".0%",
#             color="white",
#             gridcolor="rgba(255,255,255,0.08)"
#         ),

#         yaxis=dict(
#             color="white",
#             automargin=True
#         )
#     )

#     graph_html = fig2.to_html(
#         full_html=False,
#         include_plotlyjs='cdn',
#         config={
#             'displayModeBar': False
#         }
#     )

#     with chart_container:

#         components.html(
#             f"""
#             <div style="
#                 height:500px;
#                 overflow-y:auto;
#                 overflow-x:hidden;
#                 border-radius:10px;
#                 background:#0E1117;
#                 padding:5px;
#             ">
#                 {graph_html}
#             </div>
#             """,
#             height=520,
#             scrolling=False
#         )



def estilo_media(valor):
    if pd.isna(valor):
        return ""
    if valor >= 0.85:
        return "color: #22C55E; font-weight: 700;"
    if valor >= 0.70:
        return "color: #FDBA3B; font-weight: 700;"
    return "color: #FF4B4B; font-weight: 700;"


col1, col2, col3 = st.columns(3)

# ======================================================
# LOJAS
# ======================================================

with col1:

    loja_rank = (
        df_filtrado
        .groupby("Loja", as_index=False)
        .agg({
            "Nota Atingida": "sum",
            "Nota Possível": "sum"
        })
    )

    loja_rank["Média"] = (
        loja_rank["Nota Atingida"] /
        loja_rank["Nota Possível"]
    )

    loja_rank = loja_rank.sort_values(
        by="Média",
        ascending=False
    )

    loja_table = (
        loja_rank[["Loja", "Média"]]
        .style
        .format({"Média": "{:.2%}"})
        .map(estilo_media, subset=["Média"])
        .set_table_styles([
            {"selector": "th", "props": [("font-weight", "700")]},
            {"selector": "td", "props": [("font-weight", "700")]}
        ])
    )

    st.dataframe(
        loja_table,
        use_container_width=True,
        height=320,
        hide_index=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# TÓPICOS
# ======================================================

with col2:

    topico_rank = (
        df_filtrado
        .groupby("Tópico", as_index=False)
        .agg({
            "Nota Atingida": "sum",
            "Nota Possível": "sum"
        })
    )

    topico_rank["Média"] = (
        topico_rank["Nota Atingida"] /
        topico_rank["Nota Possível"]
    )

    topico_rank = topico_rank.sort_values(
        by="Média",
        ascending=False
    )


    topico_table = (
        topico_rank[["Tópico", "Média"]]
        .style
        .format({"Média": "{:.2%}     "})
        .map(estilo_media, subset=["Média"])
        .set_table_styles([
            {"selector": "th", "props": [("font-weight", "700")]},
            {"selector": "td", "props": [("font-weight", "700")]}
        ])
    )

    st.dataframe(
        topico_table,
        column_config={
            "Média": st.column_config.Column(width=200),
        },
        use_container_width=True,
        height=320,
        hide_index=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# TAGS
# ======================================================

with col3:

    tag_rank = (
        df_filtrado
        .groupby("Tag", as_index=False)
        .agg({
            "Nota Atingida": "sum",
            "Nota Possível": "sum"
        })
    )

    tag_rank["Média"] = (
        tag_rank["Nota Atingida"] /
        tag_rank["Nota Possível"]
    )

    tag_rank = tag_rank.sort_values(
        by="Média",
        ascending=False
    )

    tag_table = (
        tag_rank[["Tag", "Média"]]
        .style
        .format({"Média": "{:.2%}"})
        .map(estilo_media, subset=["Média"])
        .set_table_styles([
            {"selector": "th", "props": [("font-weight", "700")]},
            {"selector": "td", "props": [("font-weight", "700")]}
        ])
    )



    st.dataframe(
        tag_table,
        use_container_width=True,
        height=320,
        hide_index=True

    )

    st.markdown('</div>', unsafe_allow_html=True)


col1 = st.columns(1)


# =========================================================
# Tabela Geral
# =========================================================

with col1[0]:

    st.subheader("Tabela Geral")

    tabela_geral_base = df_filtrado[[
        "Data", "Loja", "Tópico", "Tag", "Questão", "Resposta", "Observação"
    ]]

    tabela_geral_base['Data'] = tabela_geral_base['Data'].dt.strftime('%d/%m/%Y')

    total_rows = len(tabela_geral_base)
    pager_cols = st.columns([1, 1, 2])

    pager_cols[0].markdown(
        '<div class="pager-label">Linhas por pagina</div>',
        unsafe_allow_html=True
    )
    rows_per_page = pager_cols[0].selectbox(
        "",
        [10, 20, 50, 100],
        index=1,
        key="tabela_geral_rows",
        label_visibility="collapsed"
    )

    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)
    pager_cols[1].markdown(
        '<div class="pager-label">Pagina</div>',
        unsafe_allow_html=True
    )
    page = pager_cols[1].number_input(
        "",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
        key="tabela_geral_page",
        label_visibility="collapsed"
    )

    pager_cols[2].markdown(
        f"Pagina {page} de {total_pages} | {total_rows} linhas"
    )

    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    tabela_geral = tabela_geral_base.iloc[start:end]

    st.dataframe(
        tabela_geral,
        use_container_width=True,
        height=400,
        hide_index=True
    )
