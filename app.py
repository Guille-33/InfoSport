from __future__ import annotations

import streamlit as st
import pandas as pd
import time
from collections.abc import Iterator

from config import TOP_K
from src.logic import responder

def generar_mensaje(message: dict) -> None:
    with st.chat_message(message["role"]):
        if message.get("error"):
            st.error(message["content"])
        else:
            st.markdown(message["content"])

        if message.get("fuentes"):
            st.markdown("**Fuentes**")
            for fuente in message["fuentes"]:
                st.write(f"- `{fuente}`")

        if message.get("contexto"):
            with st.expander("Contexto recuperado (debug)"):
                st.text(message["contexto"])

def inicio(nombre: str) -> dict:
    return {
        "role": "assistant",
        "content": (
            f"Hola — soy **{nombre}**. "
            "Pregúntame sobre las competiciones deportivas en Madrid, también puedo responder preguntas de normativa de polideportivos. "
            "Cada turno consulta el índice RAG (`src.logic.responder`); "
            "no reutilizo el hilo como contexto del modelo."
        ),
        "fuentes": [],
        "contexto": "",
        "error": False,
    }

def stream_palabras(texto: str, delay: float = 0.02) -> Iterator[str]:
    """Genera el texto palabra a palabra (efecto 'máquina de escribir').

    Streamlit usa este generador con `st.write_stream` para mostrar la
    respuesta de forma gradual. No cambia el contenido: solo la presentación.
    """
    for palabra in texto.split():
        yield palabra + " "
        time.sleep(delay)

st.set_page_config(
    page_title="Asistente competición deportiva Madrid",
    page_icon="🏃",
    layout="centered",
)

with st.sidebar:
    st.header("Configuración")
    nombre = st.text_input("Nombre del bot", value="Asistente deportivo")
    top_k = st.slider("Top-K", min_value=1, max_value=5, value=TOP_K)
    st.caption("`TOP_K`: numero de fragmentos a recuperar")
    if st.button("Limpiar chat", use_container_width=True):
        st.session_state.messages = [inicio(nombre)]
        st.rerun()

st.title(nombre)
st.caption("Ayuda en busqueda de tablas clasificatorias y normas de la Comunidad")

datos_metricas={
    'metricas':['TOP_k','tiempo'],
    'valores': [top_k]
}

if "messages" not in st.session_state:
    st.session_state.messages = [inicio(nombre)]

# Repintar todo el hilo en cada ejecución del script
for message in st.session_state.messages:
    generar_mensaje(message)

if prompt := st.chat_input("Tu pregunta sobre la agenda cultural…"):
    # 1) Guardar y mostrar la pregunta
    t_ini=time.time()
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "fuentes": [], "contexto": "", "error": False}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2) Llamar al backend RAG (una pregunta → un dict; sin memoria de conversación)
    with st.chat_message("assistant"):
        with st.status("Consultando el corpus…", expanded=False) as status:
            resultado = responder(pregunta=prompt, top_k=top_k)
            status.update(label="Listo", state="complete")

        if resultado.get("error"):
            # Validación, índice vacío, API, etc. → mensaje amigable
            st.error(resultado["error"])
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": resultado["error"],
                    "fuentes": resultado.get("fuentes") or [],
                    "contexto": resultado.get("contexto") or "",
                    "error": True,
                }
            )
        else:
            escrito = st.write_stream(stream_palabras(resultado["respuesta"]))
            contenido = escrito if isinstance(escrito, str) else resultado["respuesta"]

            if resultado.get("fuentes"):
                st.markdown("**Fuentes**")
                for fuente in resultado["fuentes"]:
                    st.write(f"- `{fuente}`")

            if resultado.get("contexto"):
                with st.expander("Contexto recuperado (debug)"):
                    st.text(resultado["contexto"])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": contenido,
                    "fuentes": resultado.get("fuentes") or [],
                    "contexto": resultado.get("contexto") or "",
                    "error": False,
                }
            )
    datos_metricas.get('valores',[]).append(time.time()-t_ini)
    df = pd.DataFrame(datos_metricas)
    st.subheader("Métricas de Rendimiento Mensual")
    st.dataframe(df, width="stretch", hide_index=True)
