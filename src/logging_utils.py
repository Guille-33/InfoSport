# src/logging_utils.py
from datetime import datetime
import json
import os
from config import LOG_FILE_JSON

def registrar_consulta_json(*,pregunta: str, k: int, num_chunks: int, tiempo_ejecucion: float, modelo: str,modelo_embedding:str, se_abstuvo: bool):
    # 1. Crear el diccionario estructurado con los datos obligatorios
    registro = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pregunta": pregunta,
        "configuracion": {
            "k_solicitado": k,
            "modelo_llm": modelo,
            "modelo_embedding":modelo_embedding
        },
        "metricas": {
            "chunks_recuperados": num_chunks,
            "tiempo_respuesta_segundos": round(tiempo_ejecucion, 3),
            "abstencion": se_abstuvo
        }
    }
    
    # 2. Leer datos existentes o inicializar lista vacía
    datos_existentes = []
    if os.path.exists(LOG_FILE_JSON):
        try:
            with open(LOG_FILE_JSON, "r", encoding="utf-8") as f:
                datos_existentes = json.load(f)
        except json.JSONDecodeError:
            # Por si el archivo se quedó corrupto o vacío en alguna prueba anterior
            datos_existentes = []

    # 3. Añadir el nuevo registro a la lista
    datos_existentes.append(registro)

    # 4. Guardar de nuevo todo el historial formateado en el JSON
    with open(LOG_FILE_JSON, "w", encoding="utf-8") as f:
        json.dump(datos_existentes, f, ensure_ascii=False, indent=4)
