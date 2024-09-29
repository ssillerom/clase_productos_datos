import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Configuración de la página
st.set_page_config(page_title="Valley: Recogidas de Uber en NYC", layout="wide")

# Título y descripción
st.title("🚕 Recogidas de Valley-Uber en NYC")
st.markdown(
    """
    ### Una aplicación que muestra las recogidas de Uber en Nueva York distribuidas geográficamente.
    Datos recogidos durante el mes de septiembre de 2014.
    """
)

# Cargar datos
DATE_TIME = "date/time"
DATA_URL = "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"

@st.cache_data(persist=True)
def load_data(number_rows):
    df = pd.read_csv(DATA_URL, nrows=number_rows)
    df.rename(str.lower, axis="columns", inplace=True)
    df[DATE_TIME] = pd.to_datetime(df[DATE_TIME])
    return df

data = load_data(100000)
midpoint = (np.average(data["lat"]), np.average(data["lon"]))

# Sidebar para seleccionar la hora
st.sidebar.header("Configuración")
hora = st.sidebar.slider('Selecciona la hora:', 0, 23, 6)
filtered_data = data[data[DATE_TIME].dt.hour == hora]

# Mostrar datos geoespaciales
st.write(f'## Datos geoespaciales a las {hora}:00 horas')

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=11,
        pitch=50
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=filtered_data,
           get_position='[lon, lat]',
           radius=100,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True
        )
    ]
))

# Mostrar tabla de datos
if st.sidebar.checkbox('Mostrar tabla de datos'):
    st.write("### Tabla de datos filtrados")
    st.dataframe(filtered_data)

# Pie de página
st.markdown(
    """
    ---
    **Desarrollado por Sergio Sillero**
    """
)
