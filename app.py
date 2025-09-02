import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import json
import unicodedata

# ----------------- FUNCIONES -----------------
def normalizar(texto):
    if pd.isna(texto):
        return texto
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto.upper().strip()

@st.cache_data
def load_data():
    df = pd.read_csv("data/pensionados_publico.csv", dtype={"CP": str})
    with open("data/geo/10-Dgo.geojson", "r", encoding="utf-8") as f:
        durango_geo = json.load(f)
    return df, durango_geo

# ----------------- CARGA DE DATOS -----------------
df, durango_geo = load_data()
df['MUNICIPIO'] = df['MUNICIPIO'].apply(normalizar)

cobertura = [
    'DURANGO',
    'PANUCO DE CORONADO',
    'SAN JUAN DEL RIO',
    'CANATLAN',
    'NOMBRE DE DIOS',
    'VICENTE GUERRERO',
    'POANAS',
    'MEZQUITAL',
    'SUCHIL',
    'GUADALUPE VICTORIA'
]

con_cobertura = df[df['MUNICIPIO'].isin(cobertura)]
df_durango = con_cobertura[con_cobertura["MUNICIPIO"] == "DURANGO"]

# ----------------- GRAFICAS -----------------
# 1. Mapa Durango (por CP)
cp_counts = df_durango.groupby("CP").size().reset_index(name="conteo")
custom_colors = ["#00000f", "#00314e", "#00689b", "#00a9f4", "#00f3ff"]

fig_mapa = px.choropleth_mapbox(
    cp_counts,
    geojson=durango_geo,
    locations="CP",
    featureidkey="properties.d_codigo",
    color="conteo",
    color_continuous_scale=custom_colors,
    mapbox_style="carto-positron",
    zoom=11,
    center={"lat": 24.0277, "lon": -104.6532},
    opacity=0.6,
    labels={"conteo": "Número de pensionados"}
)

# 2. Municipios sin Durango (barh)
otros_mpios = con_cobertura[con_cobertura["MUNICIPIO"] != "DURANGO"]
mpio_counts = otros_mpios["MUNICIPIO"].value_counts()

fig_mpios, ax1 = plt.subplots(figsize=(10, 5))
mpio_counts.plot(kind="barh", color="teal", ax=ax1)
ax1.set_title("Distribución de pensionados por municipio (sin Durango)")
ax1.set_xlabel("Número de pensionados")
ax1.set_ylabel("Municipio")
plt.tight_layout()

# 3. Distribución de edades
df['EDAD_GRUPO'] = pd.cut(df['EDAD'], bins=range(30, 101, 10))
edad_counts = df['EDAD_GRUPO'].value_counts().sort_index()

fig_edades, ax2 = plt.subplots(figsize=(8, 5))
edad_counts.plot(kind="bar", color="royalblue", ax=ax2)
ax2.set_title("Distribución de pensionados por rango de edad")
ax2.set_xlabel("Rango de edad")
ax2.set_ylabel("Número de pensionados")
plt.tight_layout()

# 4. Tipo de pensión (pie chart)
tipo_counts = con_cobertura['TIPO PENSION'].value_counts().reset_index()
tipo_counts.columns = ['TIPO PENSION', 'conteo']

fig_pension = px.pie(
    tipo_counts,
    names='TIPO PENSION',
    values='conteo',
    title='Distribución por Tipo de Pensión',
    hole=0.3,
    color_discrete_sequence=px.colors.qualitative.Set3
)

# ----------------- STREAMLIT UI -----------------
st.title("Análisis de Pensionados en Durango")

opcion = st.sidebar.selectbox(
    "Selecciona la visualización",
    [
        "Mapa Durango (CP)",
        "Municipios sin Durango",
        "Distribución de edades",
        "Distribución por tipo de pensión"
    ]
)

if opcion == "Mapa Durango (CP)":
    st.plotly_chart(fig_mapa, use_container_width=True)

elif opcion == "Municipios sin Durango":
    st.pyplot(fig_mpios)

elif opcion == "Distribución de edades":
    st.pyplot(fig_edades)

elif opcion == "Distribución por tipo de pensión":
    st.plotly_chart(fig_pension, use_container_width=True)

