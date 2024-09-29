import cv2
import streamlit as st
from ultralytics import YOLO
import tempfile
import os

def app():
    # Configuración de la página de Streamlit
    st.set_page_config(page_title="The Valley: Detección de objetos", page_icon="🔍", layout="wide")

    # Título y subtítulo de la aplicación
    st.title('🔍 Detección de Objetos Web App')
    st.subheader('Desarrollado por YOLOv8')
    st.write('¡Bienvenido! Sube un video y selecciona los objetos a detectar.')

    # Cargar el modelo YOLOv8
    model = YOLO('yolov8n.pt')
    object_names = list(model.names.values())  # Obtener los nombres de los objetos que el modelo puede detectar

    # Crear un formulario para subir el video y seleccionar los objetos a detectar
    with st.form("my_form"):
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("Subir video", type=['mp4'])  # Subir archivo de video
        with col2:
            selected_objects = st.multiselect('Elige objetos a detectar', object_names, default=['person'])  # Seleccionar objetos
            min_confidence = st.slider('Indice de confianza', 0.0, 1.0, 0.5)  # Seleccionar índice de confianza
        submit_button = st.form_submit_button(label='Enviar')  # Botón para enviar el formulario
            
    # Procesar el video si se ha subido un archivo y se ha enviado el formulario
    if uploaded_file is not None and submit_button: 
        input_path = uploaded_file.name
        file_binary = uploaded_file.read()
        with open(input_path, "wb") as temp_file:
            temp_file.write(file_binary)  # Guardar el archivo subido temporalmente
        video_stream = cv2.VideoCapture(input_path)  # Abrir el video
        width = int(video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)) 
        height = int(video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
        fourcc = cv2.VideoWriter_fourcc(*'h264') 
        fps = int(video_stream.get(cv2.CAP_PROP_FPS)) 

        # Crear un archivo temporal para el video de salida
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output_file:
            output_path = temp_output_file.name

        out_video = cv2.VideoWriter(output_path, int(fourcc), fps, (width, height))  # Inicializar el escritor de video

        progress_bar = st.progress(0)  # Barra de progreso
        frame_count = int(video_stream.get(cv2.CAP_PROP_FRAME_COUNT))
        processed_frames = 0

        # Procesar cada frame del video
        with st.spinner('Procesando video...'): 
            while True:
                ret, frame = video_stream.read()
                if not ret:
                    break
                result = model(frame)  # Realizar la detección de objetos
                for detection in result[0].boxes.data:
                    x0, y0 = (int(detection[0]), int(detection[1]))
                    x1, y1 = (int(detection[2]), int(detection[3]))
                    score = round(float(detection[4]), 2)
                    cls = int(detection[5])
                    object_name =  model.names[cls]
                    label = f'{object_name} {score}'

                    # Dibujar rectángulos y etiquetas en los objetos detectados
                    if model.names[cls] in selected_objects and score > min_confidence:
                        cv2.rectangle(frame, (x0, y0), (x1, y1), (255, 0, 0), 2)
                        cv2.putText(frame, label, (x0, y0 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
                # Mostrar el número de detecciones en el frame
                detections = result[0].verbose()
                cv2.putText(frame, detections, (10, 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir el frame a RGB
                out_video.write(frame)  # Escribir el frame en el video de salida

                processed_frames += 1
                progress_bar.progress(processed_frames / frame_count)  # Actualizar la barra de progreso

            video_stream.release()  # Liberar el video de entrada
            out_video.release()  # Liberar el video de salida
        st.video(output_path)  # Mostrar el video procesado en la aplicación
        os.remove(output_path)  # Limpiar el archivo temporal

if __name__ == "__main__":
    app()  # Ejecutar la aplicación