# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 10:38:15 2026

@author: kennk
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import FuncFormatter

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
    
    df_internos['CUSTO_HORA'] = np.where(
        df_internos['CARGA_HORARIA'] > 0,
        df_internos['VALOR_EMPENHADO'] / df_internos['CARGA_HORARIA'],
        np.nan
    )

    df_externos['CUSTO_HORA'] = np.where(
        df_externos['CARGA_HORARIA'] > 0,
        df_externos['VALOR_EMPENHADO'] / df_externos['CARGA_HORARIA'],
        np.nan
    )

    for df in [df_internos, df_externos]:

        if "ANO_PDP" in df.columns:
            df["ANO_PDP"] = pd.to_numeric(
                df["ANO_PDP"],
                errors="coerce"
            )
            
        

    return df_internos, df_externos


df_internos, df_externos = carregar_dados()

# =====================================================
# FILTROS
# =====================================================

tipo = st.sidebar.radio(
    "Tipo de Capacitação",
    ["Internos", "Externos"]
)

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

# =====================================================
# KPIs
# =====================================================

total_acoes = df_filtro["ACAO_DE_DESENVOLVIMENTO"].count()

total_participantes = df_filtro["SIAPE"].nunique()

valor_total = df_filtro["VALOR_EMPENHADO"].sum()

carga_media = df_filtro["CARGA_HORARIA"].mean()

valor_aluno = df_filtro["VALOR_PAGO_POR_ALUNO"].mean()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Ações",
    f"{total_acoes:,.0f}"
)

c2.metric(
    "Participantes",
    f"{total_participantes:,.0f}"
)

c3.metric(
    "Valor Empenhado",
    f"R$ {valor_total/1_000_000:,.2f} Mi"
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
        df_filtro
        .groupby("MODALIDADE")["VALOR_EMPENHADO"]
        .sum()
        .reset_index()
    )

    total = dados["VALOR_EMPENHADO"].sum()

    fig = px.pie(
        dados,
        names="MODALIDADE",
        values="VALOR_EMPENHADO",
        hole=0.70,
        title="Valor Empenhado por Modalidade"
    )

    fig.add_annotation(
        text=f"<b>R$ {total/1_000_000:.2f} Mi</b>",
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
    use_container_width=True
    )

with col2:

    participantes_secretaria = (
        df_filtro
        .groupby("SECRETARIA_DE_LOTACAO")["SIAPE"]
        .nunique()
        .reset_index()
        .sort_values("SIAPE")
    )

    fig = px.bar(
        participantes_secretaria,
        x="SIAPE",
        y="SECRETARIA_DE_LOTACAO",
        orientation="h",
        title="Participantes por Secretaria"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

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
        title="Ações por Tipo"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    custo_secretaria = (
        df_filtro
        .groupby("SECRETARIA_DE_LOTACAO")
        ["VALOR_EMPENHADO"]
        .sum()
        .reset_index()
        .sort_values("VALOR_EMPENHADO")
    )

    fig = px.bar(
        custo_secretaria,
        x="VALOR_EMPENHADO",
        y="SECRETARIA_DE_LOTACAO",
        orientation="h",
        title="Valor Empenhado por Secretaria"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# LINHA 3
# =====================================================

metricas = (
    df_filtro
    .groupby("SECRETARIA_DE_LOTACAO")
    .agg({
        "CARGA_HORARIA":"mean",
        "VALOR_PAGO_POR_ALUNO":"mean"
    })
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        metricas.sort_values("CARGA_HORARIA"),
        x="CARGA_HORARIA",
        y="SECRETARIA_DE_LOTACAO",
        orientation="h",
        title="Carga Horária Média"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.bar(
        metricas.sort_values("VALOR_PAGO_POR_ALUNO"),
        x="VALOR_PAGO_POR_ALUNO",
        y="SECRETARIA_DE_LOTACAO",
        orientation="h",
        title="Valor Médio por Aluno"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# LINHA 4
# =====================================================

st.subheader("Análise por Tipo de Ação")

indicador_tipo = st.radio(
    "",
    [
        "Valor Empenhado por Tipo de Ação",
        "Participantes por Tipo de Ação"
    ],
    horizontal=True
)

col1, col2 = st.columns(2)

with col1:

    if indicador_tipo == "Valor Empenhado por Tipo de Ação":

        dados = pd.pivot_table(
            df_filtro,
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

        st.plotly_chart(
            fig,
            use_container_width=True
        )        

with col2:

   custo_hora = (
    df_filtro
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
       text_auto=".2f"
     )

   fig.update_layout(
    xaxis_title="R$/Hora",
    yaxis_title=""
)

   st.plotly_chart(
       fig,
       use_container_width=True
)
