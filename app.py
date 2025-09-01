import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pensionados Durango", layout="wide")
st.title("📊 Análisis de Pensionados en Durango")

@st.cache_data
def load_data():
    # lee la versión pública/anonimizada
    return pd.read_csv("data/pensionados_publico.csv", dtype={"CP": str})

df = load_data()

st.subheader("Vista previa")
st.dataframe(df.head(), use_container_width=True)

st.subheader("Pensionados por ciudad")
conteo = df["CIUDAD"].value_counts().reset_index()
conteo.columns = ["Ciudad", "Pensionados"]
fig = px.bar(conteo, x="Ciudad", y="Pensionados", title="Número de pensionados por ciudad")
st.plotly_chart(fig, use_container_width=True)
