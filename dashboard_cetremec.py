# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 10:38:15 2026

@author: kennk
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Dashboard CETREMEC",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LEITURA DA BASE
# =====================================================

@st.cache_data
def carregar_dados():

    file = "DADOS CETREMEC.xlsx"

    df_internos = pd.read_excel(
        file,
        sheet_name="Internos",
        engine="openpyxl"
    )

    df_externos = pd.read_excel(
        file,
        sheet_name="Externos",
        engine="openpyxl"
    )


    for df in [df_internos, df_externos]:

        if "ANO_PDP" in df.columns:
            df["ANO_PDP"] = pd.to_numeric(
                df["ANO_PDP"],
                errors="coerce"
            )
            
        

    return df_internos, df_externos


df_internos, df_externos = carregar_dados()

df_internos["SECRETARIA_DE_LOTACAO"] = (
    df_internos["SECRETARIA_DE_LOTACAO"]
    .str.strip()
)

df_externos["SECRETARIA_DE_LOTACAO"] = (
    df_externos["SECRETARIA_DE_LOTACAO"]
    .str.strip()
)

# =====================================================
# FILTROS
# =====================================================

tipo = st.sidebar.radio(
    "Tipo de Capacitação",
    ["Internos", "Externos"]
)

with st.sidebar.expander("📱 Como utilizar o Dashboard"):

    st.markdown("""
### Navegação

🔹 Selecione **Internos** ou **Externos**.

🔹 Utilize os filtros de:
- Ano
- Secretaria
- Modalidade
- Tipo de Indicador

🔹 Todos os gráficos são atualizados automaticamente.

### Celular

📱 Em dispositivos móveis:

- Toque uma vez no gráfico para ativar a interação.
- Arraste para navegar pelo gráfico.
- Utilize dois dedos para zoom.
- Toque duas vezes fora do gráfico para retornar à navegação da página.

### Dicas

📊 Passe o dedo sobre os gráficos para visualizar valores.

📈 Utilize os filtros para comparar indicadores.

📋 Consulte a tabela de detalhamento ao final da página.
""")

if tipo == "Internos":
    df_base = df_internos.copy()
else:
    df_base = df_externos.copy()
st.title("📊 Dashboard CETREMEC")

col1, col2, col3 = st.columns(3)

with col1:
    ano = st.multiselect(
        "Ano",
        sorted(df_base["ANO_PDP"].dropna().unique()),
        default=sorted(df_base["ANO_PDP"].dropna().unique())
    )

with col2:
    secretaria = st.multiselect(
        "Secretaria",
        sorted(df_base["SECRETARIA_DE_LOTACAO"].dropna().unique()),
        default=[]
    )

with col3:
    modalidade = st.multiselect(
        "Modalidade",
        sorted(df_base["MODALIDADE"].dropna().unique()),
        default=[]
    )

df_filtro = df_base.copy()

if ano:
    df_filtro = df_filtro[df_filtro["ANO_PDP"].isin(ano)]

if secretaria:
    df_filtro = df_filtro[
        df_filtro["SECRETARIA_DE_LOTACAO"].isin(secretaria)
    ]

if modalidade:
    df_filtro = df_filtro[
        df_filtro["MODALIDADE"].isin(modalidade)
    ]
    

df_financeiro = (
    df_filtro
    .drop_duplicates(subset="NOTA_DE_EMPENHO_CREDITO", keep="first")
)


# =====================================================
# KPIs
# =====================================================

total_acoes = df_filtro["ACAO_DE_DESENVOLVIMENTO"].count()

total_participantes = df_filtro["SIAPE"].nunique()

valor_total = df_financeiro["VALOR_EMPENHADO"].sum()

carga_media = df_filtro["CARGA_HORARIA"].mean()

valor_aluno = df_financeiro["VALOR_PAGO_POR_ALUNO"].mean()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Ações",
    f"{total_acoes:,.0f}"
)

c2.metric(
    "Participantes",
    f"{total_participantes:,.0f}"
)

def formatar_valor_empenhado(valor):
    if valor >= 1_000_000:
        return f"R$ {valor/1_000_000:.2f} Mi"
    elif valor >= 1_000:
        return f"R$ {valor/1_000:.2f} k"
    else:
        return f"R$ {valor:,.2f}"

c3.metric(
    "Valor Empenhado",
    formatar_valor_empenhado(valor_total)
)

c4.metric(
    "Carga Horária Média",
    f"{carga_media:,.2f}"
)

c5.metric(
    "Valor Médio por Aluno",
    f"R$ {valor_aluno:,.2f}"
)

st.divider()



# =====================================================
# LINHA 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

   indicador = st.segmented_control(
    "Indicador",
    ["Participantes", "Valor Empenhado"],
    default="Participantes"
)
   
   
   if indicador == "Participantes":

    dados = (
        df_filtro
        .groupby("MODALIDADE")["SIAPE"]
        .nunique()
        .reset_index()
    )

    total = dados["SIAPE"].sum()

    fig = px.pie(
        dados,
        names="MODALIDADE",
        values="SIAPE",
        hole=0.70,
        title="Participantes por Modalidade"
    )

    fig.add_annotation(
        text=f"<b>{total:,}</b><br>Participantes",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=20)
    )

   else:

    dados = (
        df_financeiro
        .groupby("MODALIDADE")["VALOR_EMPENHADO"]
        .sum()
        .reset_index()
    )

    total = df_financeiro["VALOR_EMPENHADO"].sum()   # número

    total_formatado = formatar_valor_empenhado(total)  # texto

    fig = px.pie(
        dados,
        names="MODALIDADE",
        values="VALOR_EMPENHADO",
        hole=0.70,
        title="Valor Empenhado por Modalidade"
    )

    fig.add_annotation(
        text=f"<b>{formatar_valor_empenhado(total)}</b>",
        x=0.5,
        y=0.5,
       showarrow=False,
        font=dict(size=20)
    )

   fig.update_layout(
    showlegend=False
    )


   fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
    )

   st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": False}
    )

with col2:
    st.markdown("##### 🏛️ Análise por Secretaria")

    opcao_secretaria = st.segmented_control(
        label="Indicador",
        options=["👥 Participantes", "💰 Valor Empenhado"],
        default="👥 Participantes",
        key="indicador_secretaria"
    )
    if opcao_secretaria == "👥 Participantes":

        df_secretaria = (
            df_filtro
            .groupby("SECRETARIA_DE_LOTACAO")["SIAPE"]
            .nunique()
            .reset_index(name="Participantes")
            .sort_values("Participantes")
    )

        fig = px.bar(
            df_secretaria,
            x="Participantes",
            y= 'SECRETARIA_DE_LOTACAO',
            orientation="h",
            text_auto=True,
            color="Participantes",
            color_continuous_scale="Blues"
    )
    else:
        df_secretaria = (
            df_financeiro
            .groupby("SECRETARIA_DE_LOTACAO")["VALOR_EMPENHADO"]
            .sum()
            .reset_index()
            .sort_values("VALOR_EMPENHADO")
            )

        fig = px.bar(
            df_secretaria,
            x="VALOR_EMPENHADO",
            y="SECRETARIA_DE_LOTACAO",
            orientation="h",
            text_auto=".2s",
            color="VALOR_EMPENHADO",
            color_continuous_scale="Greens"
            )

    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False
        )

    st.plotly_chart(fig, use_container_width=True)



# =====================================================
# LINHA 2
# =====================================================

col1, col2 = st.columns(2)

with col1:

    tipo_acao = (
        df_filtro["TIPO_DE_ACAO"]
        .value_counts()
        .reset_index()
    )

    tipo_acao.columns = [
        "TIPO_DE_ACAO",
        "QTD"
    ]

    fig = px.bar(
        tipo_acao.sort_values("QTD"),
        x="QTD",
        y="TIPO_DE_ACAO",
        orientation="h",
        title="Ações por Tipo",
        color="QTD",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False
        )
    

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": False}
    )

metricas = (
    df_financeiro
    .groupby("SECRETARIA_DE_LOTACAO")
    .agg({
        "CARGA_HORARIA":"mean",
        "VALOR_PAGO_POR_ALUNO":"mean"
    })
    .reset_index()
)

with col2:
    fig = px.bar(
        metricas.sort_values("CARGA_HORARIA"),
        x="CARGA_HORARIA",
        y="SECRETARIA_DE_LOTACAO",
        orientation="h",
        title="Carga Horária Média",
        color="CARGA_HORARIA",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False
        )
    
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
# =====================================================
# LINHA 3
# =====================================================


col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        metricas.sort_values("VALOR_PAGO_POR_ALUNO"),
        x="VALOR_PAGO_POR_ALUNO",
        y="SECRETARIA_DE_LOTACAO",
        orientation="h",
        title="Valor Médio por Aluno",
        color="VALOR_PAGO_POR_ALUNO",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False
        )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": False}
    )
    

df_financeiro['CUSTO_HORA'] = np.where(
    df_financeiro['CARGA_HORARIA'] > 0,
    df_financeiro['VALOR_EMPENHADO'] / df_financeiro['CARGA_HORARIA'],
    np.nan
)


with col2:
   custo_hora = (
    df_financeiro
    .groupby("SECRETARIA_DE_LOTACAO")["CUSTO_HORA"]
    .mean()
    .reset_index()
    .sort_values("CUSTO_HORA", ascending=True)
    )

   fig = px.bar(
       custo_hora,
       x="CUSTO_HORA",
       y="SECRETARIA_DE_LOTACAO",
       orientation="h",
       title="Custo Hora por Secretaria",
       text_auto=".2f",
       color="CUSTO_HORA",
       color_continuous_scale="Blues"
     )
   
   fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False
        )

   fig.update_layout(
    xaxis_title="R$/Hora",
    yaxis_title=""
)

   st.plotly_chart(
       fig,
       use_container_width=True,
       config={"scrollZoom": False}
)

# =====================================================
# LINHA 4
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Análise por Tipo de Ação")

    indicador_tipo = st.radio(
        "",
        [
            "Valor Empenhado por Tipo de Ação",
            "Participantes por Tipo de Ação"
        ],
        horizontal=True
    )
    if indicador_tipo == "Valor Empenhado por Tipo de Ação":

        dados = pd.pivot_table(
            df_financeiro,
            values="VALOR_EMPENHADO",
            index="SECRETARIA_DE_LOTACAO",
            columns="TIPO_DE_ACAO",
            aggfunc="mean"
        ).fillna(0)

        fig = px.bar(
            dados.reset_index(),
            y="SECRETARIA_DE_LOTACAO",
            x=dados.columns,
            orientation="h",
            title="Valor Empenhado por Tipo de Ação e Secretaria"
        )
        
        fig.update_layout(
             height=450,
             margin=dict(l=10, r=10, t=30, b=10),
             coloraxis_showscale=False
             )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        
    else:
        dados = pd.pivot_table(
            df_filtro,
            values="SIAPE",
            index="SECRETARIA_DE_LOTACAO",
            columns="TIPO_DE_ACAO",
            aggfunc="nunique"
        ).fillna(0)

        fig = px.bar(
            dados.reset_index(),
            y="SECRETARIA_DE_LOTACAO",
            x=dados.columns,
            orientation="h",
            title="Participantes por Tipo de Ação e Secretaria"
        )
        
        fig.update_layout(
             height=450,
             margin=dict(l=10, r=10, t=30, b=10),
             coloraxis_showscale=False
             )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"scrollZoom": False}
        )        

with col2:
    st.subheader("Evolução Mensal dos Valores")


    df_filtro["MES_EMPENHO"] = (
        df_filtro["MES_EMPENHO"].astype(str).str.strip().str.upper()
        )
    df_filtro["MES_PAGAMENTO"] = (
        df_filtro["MES_PAGAMENTO"].astype(str).str.strip().str.upper()
        )

    mapa_meses = {
        "JANEIRO": "JAN",
        "FEVEREIRO": "FEV",
        "MARÇO": "MAR",
        "ABRIL": "ABR",
        "MAIO": "MAI",
        "JUNHO": "JUN",
        "JULHO": "JUL",
        "AGOSTO": "AGO",
        "SETEMBRO": "SET",
        "OUTUBRO": "OUT",
        "NOVEMBRO": "NOV",
        "DEZEMBRO": "DEZ",
        }

    ordem_meses = [
        "JAN",
        "FEV",
        "MAR",
        "ABR",
        "MAI",
        "JUN",
        "JUL",
        "AGO",
        "SET",
        "OUT",
        "NOV",
        "DEZ",
        ]

    df_financeiro["MES_EMPENHO_SIGLA"] = df_filtro["MES_EMPENHO"].map(mapa_meses)
    df_financeiro["MES_PAGAMENTO_SIGLA"] = df_filtro["MES_PAGAMENTO"].map(mapa_meses)

    empenho = (
        df_financeiro.groupby("MES_EMPENHO_SIGLA")["VALOR_EMPENHADO"]
        .sum()
        .reindex(ordem_meses, fill_value=0)
        )

    pagamento = (
        df_financeiro.groupby("MES_PAGAMENTO_SIGLA")["VALOR_EMPENHADO"]
        .sum()
        .reindex(ordem_meses, fill_value=0)
        )   

    grafico_mensal = pd.DataFrame(
        {"Mês": ordem_meses, "Empenhado": empenho.values, "Pago": pagamento.values}
        )


    fig_mensal = go.Figure()

    fig_mensal.add_bar(
        x=grafico_mensal["Mês"],
        y=grafico_mensal["Empenhado"],
        name="Empenhado",
        marker_color="#2b7bba",
        )

    fig_mensal.add_trace(
        go.Scatter(
            x=grafico_mensal["Mês"],
            y=grafico_mensal["Pago"],
            mode="lines+markers",
            name="Pago",
            line=dict(color="#2ca02c", width=3),
            marker=dict(size=8),
            )
        )

    fig_mensal.update_layout(
        title="Evolução Mensal do Valor Empenhado x Pago (Anos Selecionados)",
        yaxis_title="Valor (R$)",
        hovermode="x unified",
        barmode="group",
        height=450,
        )

    fig_mensal.update_yaxes(tickprefix="R$ ", tickformat="..0f")

    st.plotly_chart(
        fig_mensal, use_container_width=True, config={"scrollZoom": False}
        ) 

# =====================================================
# TABELA
# =====================================================

tabela_resumo = (
    df_financeiro
    .groupby("SECRETARIA_DE_LOTACAO")
    .agg(
        Participantes=("SIAPE", "nunique"),
        Acoes=("ACAO_DE_DESENVOLVIMENTO", "count"),
        Valor_Empenhado=("VALOR_EMPENHADO", "sum"),
        Carga_Horaria_Media=("CARGA_HORARIA", "mean")
    )
    .reset_index()
)

tabela_resumo["Custo_Hora"] = (
    tabela_resumo["Valor_Empenhado"] /
    tabela_resumo["Carga_Horaria_Media"]
)

tabela_resumo["Valor_Por_Participante"] = (
    tabela_resumo["Valor_Empenhado"] /
    tabela_resumo["Participantes"]
)


tabela_exibicao = tabela_resumo.copy()

tabela_exibicao["Valor_Empenhado"] = (
    tabela_exibicao["Valor_Empenhado"]
    .map(lambda x: f"R$ {x:,.2f}")
)

tabela_exibicao["Custo_Hora"] = (
    tabela_exibicao["Custo_Hora"]
    .map(lambda x: f"R$ {x:,.2f}")
)

tabela_exibicao["Valor_Por_Participante"] = (
    tabela_exibicao["Valor_Por_Participante"]
    .map(lambda x: f"R$ {x:,.2f}")
)

tabela_exibicao["Carga_Horaria_Media"] = (
    tabela_exibicao["Carga_Horaria_Media"]
    .round(1)
)

st.subheader("📋 Indicadores por Secretaria")

st.dataframe(
    tabela_exibicao,
    use_container_width=True,
    hide_index=True
)
