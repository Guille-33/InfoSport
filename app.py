from __future__ import annotations

import streamlit as st

from config import TOP_K
from src.logic import responder

st.set_page_config(
    page_title="Asistente competición deportiva Madrid",
    page_icon="🏃",
    layout="centered",
)

st.title("Asistente")
st.caption("Ayuda en busqueda de tablas clasificatorias y normas de la Comunidad")

with st.sidebar:
    st.header("Configuración")
    top_k = st.slider("Top-K", min_value=1, max_value=5, value=TOP_K)
    st.caption("`TOP_K`: numero de fragmentos a recuperar")

consulta = st.text_input("Consulta")
enviar = st.button("Consultar", type="primary")

if enviar:
    if not (consulta or "").strip():
        st.warning("Escribe una consulta.")
    else:
        with st.spinner("Consultando el corpus…"):
            resultado = responder(pregunta=consulta.strip(), top_k=top_k)

        if resultado.get("error"):
            st.error(resultado["error"])
        else:
            st.markdown(resultado.get("respuesta") or "(sin respuesta)")
            fuentes = resultado.get("fuentes") or []
            if fuentes:
                st.markdown("**Fuentes**")
                for f in fuentes:
                    st.write(f"- `{f}`")
            if resultado.get("contexto"):
                with st.expander("Contexto recuperado (debug)"):
                    st.text(resultado["contexto"])
