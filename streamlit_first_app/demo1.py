import streamlit as st
import pandas as pd
import numpy as np

# Título y subtítulo
st.title("Este es el título")
st.header("Esto es un subtítulo")
st.write("Esto es texto con st.write :+1:")
st.markdown("""
Esto es texto con st.markdown:
Streamlit is **_really_ cool**. :sunglasses:
"""
            )

"""
Esto es una bloque de texto que se pinta de forma _mágica_:
Streamlit is **_really_ cool**. :sunglasses:
"""

# Fórmula matemática
st.latex(r'''a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
     \sum_{k=0}^{n-1} ar^k =
     a \left(\frac{1-r^{n}}{1-r}\right)
     ''')

# DataFrame
df = pd.DataFrame(
   np.random.randn(10, 5),
   columns=[f"col_{i}" for i in range(5)])

st.dataframe(df.style.highlight_max(axis=0))

# Gráfico de línea
st.line_chart(df)

# Gráfico de área
st.area_chart(df)

# Gráfico de barras
st.bar_chart(df)

# Slider
x = st.slider('Selecciona un valor para x', min_value=0, max_value=100, value=50)
st.write(f'El valor seleccionado es: {x}')

# Input de texto
nombre = st.text_input('Escribe tu nombre')
st.write(f'Hola, {nombre}!')

# Checkbox
if st.checkbox('Mostrar DataFrame'):
    st.write(df)

# Selector de opción
opcion = st.selectbox(
    'Selecciona una opción',
    ['Opción 1', 'Opción 2', 'Opción 3']
)
st.write(f'Has seleccionado: {opcion}')

# Subir archivo
archivo_subido = st.file_uploader("Sube un archivo CSV", type="csv")
if archivo_subido is not None:
    data = pd.read_csv(archivo_subido)
    st.write(data)