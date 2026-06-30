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


mapa_meses = {
    "JANEIRO": "JAN", "FEVEREIRO": "FEV", "MARÇO": "MAR", "ABRIL": "ABR",
    "MAIO": "MAI", "JUNHO": "JUN", "JULHO": "JUL", "AGOSTO": "AGO",
    "SETEMBRO": "SET", "OUTUBRO": "OUT", "NOVEMBRO": "NOV", "DEZEMBRO": "DEZ"
}
ordem_meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

if "MES_EMPENHO" in df_base.columns:
    df_base["MES_EMPENHO_SIGLA"] = df_base["MES_EMPENHO"].astype(str).str.strip().str.upper().map(mapa_meses)
if "MES_PAGAMENTO" in df_base.columns:
    df_base["MES_PAGAMENTO_SIGLA"] = df_base["MES_PAGAMENTO"].astype(str).str.strip().str.upper().map(mapa_meses)


# =====================================================
# FILTROS
# =====================================================

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

# =====================================================
# FINANCEIRO TOTAL (sem duplicar nota)
# =====================================================

df_financeiro_global = (
    df_base[
        [
            "NOTA_DE_EMPENHO_CREDITO",
            "VALOR_EMPENHADO",
            "MODALIDADE",
            "SECRETARIA_DE_LOTACAO",
            "TIPO_DE_ACAO",
            "MES_EMPENHO_SIGLA",
            "MES_PAGAMENTO_SIGLA",
            "ANO_PDP"
        ]
    ]
    .drop_duplicates(
        subset=[
            "NOTA_DE_EMPENHO_CREDITO",
            "VALOR_EMPENHADO"
        ],
        keep="first"
    )
)

df_financeiro_global["NOTA_DE_EMPENHO_CREDITO"] = (
    df_financeiro_global["NOTA_DE_EMPENHO_CREDITO"]
    .astype(str)
    .str.strip()
)


df_filtro = df_base.copy()
if ano:
    df_filtro = df_filtro[df_filtro["ANO_PDP"].isin(ano)]
if secretaria:
    df_filtro = df_filtro[df_filtro["SECRETARIA_DE_LOTACAO"].isin(secretaria)]
if modalidade:
    df_filtro = df_filtro[df_filtro["MODALIDADE"].isin(modalidade)]


df_financeiro = df_financeiro_global.copy()
if ano:
    df_financeiro = df_financeiro[df_financeiro["ANO_PDP"].isin(ano)]
if secretaria:
    df_financeiro = df_financeiro[df_financeiro["SECRETARIA_DE_LOTACAO"].isin(secretaria)]
if modalidade:
    df_financeiro = df_financeiro[df_financeiro["MODALIDADE"].isin(modalidade)]


df_carga = (
    df_filtro
    .drop_duplicates(
        subset=[
            "ACAO_DE_DESENVOLVIMENTO",
            "TIPO_DE_ACAO",
            "SECRETARIA_DE_LOTACAO",
            "CARGA_HORARIA"
        ]
    )
)
    
# =====================================================
# KPIs
# =====================================================

total_acoes = df_filtro["ACAO_DE_DESENVOLVIMENTO"].drop_duplicates().count()

total_participantes = df_filtro["ID"].nunique()

valor_total = df_financeiro["VALOR_EMPENHADO"].sum()

carga_media = df_carga["CARGA_HORARIA"].mean()

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
        .groupby("MODALIDADE")["ID"]
        .nunique()
        .reset_index()
    )

    total = total_participantes

    fig = px.pie(
        dados,
        names="MODALIDADE",
        values="ID",
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

    total = df_financeiro["VALOR_EMPENHADO"].sum()   

    total_formatado = formatar_valor_empenhado(total)  

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
            .groupby("SECRETARIA_DE_LOTACAO")["ID"]
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
        text_auto=".2f",
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
    df_carga
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
        text_auto=".2f",
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
        text_auto=".2f",
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
    

df_carga['CUSTO_HORA'] = np.where(
    df_carga['CARGA_HORARIA'] > 0,
    df_carga["VALOR_PAGO_POR_ALUNO"] / df_carga['CARGA_HORARIA'],
    np.nan
)


with col2:
   custo_hora = (
    df_carga
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
       title="Custo Hora por participantes por Secretaria",
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
            "Participantes por Tipo de Ação",
            "Carga Horária por Tipo de Ação",
            "Custo por Aluno por Tipo de Ação"
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
        
    elif indicador_tipo == "Participantes por Tipo de Ação":
        dados = pd.pivot_table(
            df_filtro,
            values="ID",
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
    elif indicador_tipo == "Carga Horária por Tipo de Ação":

        dados = pd.pivot_table(
            df_carga,
            values="CARGA_HORARIA",
            index="SECRETARIA_DE_LOTACAO",
            columns="TIPO_DE_ACAO",
            aggfunc="mean"
            ).fillna(0)

        fig = px.bar(
            dados.reset_index(),
            y="SECRETARIA_DE_LOTACAO",
            x=dados.columns,
            orientation="h",
            title="Carga Horária por Tipo de Ação e Secretaria"
            )   

        fig.update_layout(
            height=450,
            margin=dict(l=10, r=10, t=30, b=10)
            )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"scrollZoom": False}
            )
        
    elif indicador_tipo == "Custo por Aluno por Tipo de Ação":

        dados = pd.pivot_table(
            df_carga,
            values="VALOR_PAGO_POR_ALUNO",
            index="SECRETARIA_DE_LOTACAO",
            columns="TIPO_DE_ACAO",
            aggfunc="mean"
            ).fillna(0)

        fig = px.bar(
            dados.reset_index(),
            y="SECRETARIA_DE_LOTACAO",
            x=dados.columns,
            orientation="h",
            title="Valor Médio por Aluno por Tipo de Ação e Secretaria"
            )

        fig.update_layout(
            height=450,
            margin=dict(l=10, r=10, t=30, b=10)
            )

        fig.update_xaxes(title="R$/Aluno")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"scrollZoom": False}
            )

with col2:
    st.subheader("Evolução Mensal dos Valores")

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
# TABELA INDICADORES POR SECRETARIA
# =====================================================

tabela_resumo = (
    df_filtro
    .groupby("SECRETARIA_DE_LOTACAO")
    .agg(
        Participantes=("ID", "nunique"),
        Acoes=("ACAO_DE_DESENVOLVIMENTO", "nunique"),
        Valor_Aluno=("VALOR_PAGO_POR_ALUNO", "mean"),
    )
    .reset_index()
)

valor_secretaria = (
    df_financeiro
    .groupby("SECRETARIA_DE_LOTACAO")
    ["VALOR_EMPENHADO"]
    .sum()
    .reset_index(name="Valor_Empenhado")
)

valor_carga = (
    df_carga
    .groupby("SECRETARIA_DE_LOTACAO")
    ["CARGA_HORARIA"]
    .mean()
    .reset_index(name="Carga_Horaria_Media")
)

tabela_resumo = tabela_resumo.merge(valor_secretaria, on="SECRETARIA_DE_LOTACAO", how="left")
tabela_resumo = tabela_resumo.merge(valor_carga, on="SECRETARIA_DE_LOTACAO", how="left")

tabela_resumo = tabela_resumo.fillna(0)

tabela_resumo = tabela_resumo[tabela_resumo["Valor_Empenhado"] > 0]


tabela_resumo["Valor_Por_Participante"] = np.where(
    tabela_resumo["Participantes"] > 0,
    tabela_resumo["Valor_Empenhado"] / tabela_resumo["Participantes"],
    0
)

tabela_exibicao = tabela_resumo.copy()

tabela_exibicao["Valor_Aluno"] = (
    tabela_exibicao["Valor_Aluno"]
    .map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
)

tabela_exibicao["Valor_Empenhado"] = (
    tabela_exibicao["Valor_Empenhado"]
    .map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
)

tabela_exibicao["Valor_Por_Participante"] = (
    tabela_exibicao["Valor_Por_Participante"]
    .map(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
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
