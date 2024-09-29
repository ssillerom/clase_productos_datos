import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="Recogidas de Uber en NYC", layout="wide")

st.title("Recogidas de Uber en NYC")
st.markdown(
    """
    Una aplicación que muestra las recogidas de Uber en Nueva York distribuidas geográficamente.
    Datos recogidos durante el mes de septiembre de 2014.
    """
)

# LOADING DATA
DATE_TIME = "date/time"
DATA_URL = "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"

@st.cache_data(persist=True)
def load_data(number_rows):
    df = pd.read_csv(DATA_URL, nrows=number_rows)
    df.rename(str.lower, axis="columns", inplace=True)
    df[DATE_TIME] = pd.to_datetime(df[DATE_TIME])
    return df

with st.spinner('Cargando datos...'):
    data = load_data(100000)

midpoint = (np.average(data["lat"]), np.average(data["lon"]))

# Sidebar filters
hora = st.sidebar.slider('Hora:', 0, 23, 6)
fecha = st.sidebar.date_input('Fecha:', value=pd.to_datetime("2014-09-01"), min_value=pd.to_datetime("2014-09-01"), max_value=pd.to_datetime("2014-09-30"))
map_style = st.sidebar.selectbox('Estilo del mapa:', ['mapbox://styles/mapbox/light-v9', 'mapbox://styles/mapbox/dark-v9', 'mapbox://styles/mapbox/streets-v11'])

# Filter data
data = data[(data[DATE_TIME].dt.hour == hora) & (data[DATE_TIME].dt.date == fecha)]

st.write(f'## Datos geoespaciales a las {hora}h del {fecha}')

# Map visualization
st.pydeck_chart(pdk.Deck(
    map_style=map_style,
    initial_view_state=pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=11,
        pitch=50
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
           extruded=True
        )
    ]
))

# Show data table
if st.sidebar.checkbox('Mostrar tabla de datos'):
    st.write(data)

