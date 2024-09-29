import os
import tempfile
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configuración de la página de Streamlit
st.set_page_config(page_title="Valley: Chatea con Documentos", page_icon="🦜")
st.title("🦜 LangChain: Chatea con Documentos")

# Función para configurar el retriever con caché de 1 hora
@st.cache_resource(ttl="1h")
def configurar_retriever(archivos_subidos):
    # Leer documentos PDF subidos
    documentos = []
    temp_dir = tempfile.TemporaryDirectory()
    for archivo in archivos_subidos:
        temp_filepath = os.path.join(temp_dir.name, archivo.name)
        with open(temp_filepath, "wb") as f:
            f.write(archivo.getvalue())
        loader = PyPDFLoader(temp_filepath)
        documentos.extend(loader.load())

    # Dividir documentos en fragmentos más pequeños
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    divisiones = text_splitter.split_documents(documentos)

    # Crear embeddings y almacenar en una base de datos de vectores
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = DocArrayInMemorySearch.from_documents(divisiones, embeddings)

    # Definir el retriever con configuración de búsqueda
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4})

    return retriever

# Clase para manejar la visualización de tokens en Streamlit
class HandlerStream(BaseCallbackHandler):
    def __init__(self, contenedor: st.delta_generator.DeltaGenerator, texto_inicial: str = ""):
        self.contenedor = contenedor
        self.texto = texto_inicial
        self.run_id_ignore_token = None

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        # Solución para evitar mostrar la pregunta reformulada como salida
        if prompts[0].startswith("Human"):
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if self.run_id_ignore_token == kwargs.get("run_id", False):
            return
        self.texto += token
        self.contenedor.markdown(self.texto)

# Clase para manejar la impresión de resultados de recuperación en Streamlit
class HandlerImpresionRetrieval(BaseCallbackHandler):
    def __init__(self, contenedor):
        self.status = contenedor.status("**Recuperación de Contexto**")

    def on_retriever_start(self, serialized: dict, query: str, **kwargs):
        self.status.write(f"**Pregunta:** {query}")
        self.status.update(label=f"**Recuperación de Contexto:** {query}")

    def on_retriever_end(self, documentos, **kwargs):
        for idx, doc in enumerate(documentos):
            source = os.path.basename(doc.metadata["source"])
            self.status.write(f"**Documento {idx} de {source}**")
            self.status.markdown(doc.page_content)
        self.status.update(state="complete")

# Solicitar clave API de OpenAI al usuario
openai_api_key = st.sidebar.text_input("Clave API de OpenAI", type="password")
if not openai_api_key:
    st.info("Por favor, añade tu clave API de OpenAI para continuar.")
    st.stop()

# Solicitar archivos PDF al usuario
archivos_subidos = st.sidebar.file_uploader(
    label="Subir archivos PDF", type=["pdf"], accept_multiple_files=True
)
if not archivos_subidos:
    st.info("Por favor, sube documentos PDF para continuar.")
    st.stop()

# Configurar el retriever con los archivos subidos
retriever = configurar_retriever(archivos_subidos)

# Configurar memoria para conversación contextual
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=msgs, return_messages=True)

# Configurar el modelo de lenguaje y la cadena de QA
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, temperature=0.2, streaming=True
)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm, retriever=retriever, memory=memory, verbose=True
)

# Limpiar historial de mensajes si es necesario
if len(msgs.messages) == 0 or st.sidebar.button("Borrar historial de mensajes"):
    msgs.clear()
    msgs.add_ai_message("¿Cómo puedo ayudarte?")

# Mostrar mensajes anteriores en el chat
avatars = {"human": "user", "ai": "assistant"}
for msg in msgs.messages:
    st.chat_message(avatars[msg.type]).write(msg.content)

# Procesar consulta del usuario
if user_query := st.chat_input(placeholder="¡Pregunta lo que quieras!"):
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        retrieval_handler = HandlerImpresionRetrieval(st.container())
        stream_handler = HandlerStream(st.empty())
        response = qa_chain.run(user_query, callbacks=[retrieval_handler, stream_handler])
