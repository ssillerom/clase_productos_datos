import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

st.title("Análisis de Datos de Uber en Streamlit")
st.header("Visualización y Análisis de Datos")

# LOADING DATA
DATE_TIME = "date/time"
DATA_URL = "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"

@st.cache_data(persist=True)
def load_data(number_rows):
    df = pd.read_csv(DATA_URL, nrows=number_rows)
    df.rename(str.lower, axis="columns", inplace=True)
    df[DATE_TIME] = pd.to_datetime(df[DATE_TIME])
    return df

data = load_data(100000)

# Sidebar for user input
st.sidebar.header("Parámetros de Usuario")
hora = st.sidebar.slider("Hora del día", 0, 23, 11)
data = data[data[DATE_TIME].dt.hour == hora]

# Mostrar datos filtrados
st.subheader(f"Datos filtrados para las {hora}:00")
st.write(data)
st.write(f"A las {hora}:00 hay {data.shape[0]} registros.")

# Mapa de ubicaciones de Uber
st.subheader("Mapa de ubicaciones de Uber")
st.map(data)

# Histograma de viajes por minuto
st.subheader("Histograma de viajes por minuto")
hist_values = np.histogram(data[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
st.bar_chart(hist_values)

# Gráfico de dispersión de ubicaciones
st.subheader("Gráfico de dispersión de ubicaciones")
fig = px.scatter_mapbox(data, lat="lat", lon="lon", color=data[DATE_TIME].dt.minute,
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig)

# Mapa de densidad de Uber
st.subheader("Mapa de densidad de Uber")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=data["lat"].mean(),
        longitude=data["lon"].mean(),
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data,
            get_position='[lon, lat]',
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))

# Mostrar estadísticas descriptivas
st.subheader("Estadísticas descriptivas")
st.write(data.describe())