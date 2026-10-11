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
    if st.button("Limpiar chat", width='stretch'):
        st.session_state.messages = [inicio(nombre)]
        st.session_state.df_metricas = pd.DataFrame(columns=["Pregunta", "Top_K", "Tiempo (s)", "Error"])
        st.rerun()

st.title(nombre)
st.caption("Ayuda en busqueda de tablas clasificatorias y normas de la Comunidad")

if "messages" not in st.session_state:
    st.session_state.messages = [inicio(nombre)]

if "df_metricas" not in st.session_state:
    st.session_state.df_metricas = pd.DataFrame(columns=["Pregunta", "Top_K", "Tiempo (s)", "Error"])

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
            texto,resultado = responder(pregunta=prompt, top_k=top_k)
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
    tiempo_total=time.time()-t_ini
    nueva_fila=pd.DataFrame([{
        'Pregunta':prompt if len(prompt)<100 else f'{prompt[:100]}...',
        'Top_K':top_k,
        'Tiempo (s)':round(tiempo_total,3),
        'Error': resultado.get('error',None)
    }])
    st.session_state.df_metricas = pd.concat([st.session_state.df_metricas, nueva_fila], ignore_index=True)
    st.markdown("---")
    st.subheader("Rendimiento")
    st.dataframe(nueva_fila, width='stretch', hide_index=True)

if "df_metricas" in st.session_state and not st.session_state.df_metricas.empty:
    with st.sidebar:
        st.markdown("---")
        st.subheader("Log Rendimiento")
        st.dataframe(st.session_state.df_metricas, width='stretch', hide_index=True)