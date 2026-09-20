# Rutas
from pathlib import Path
PROYECT_DIR=Path(__file__).resolve().parent
DATA_DIR=PROYECT_DIR / 'data'
ENTREGABLES_DIR=PROYECT_DIR / 'entregables'
QUERIES_DIR=PROYECT_DIR / 'queries'
SRC_DIR=PROYECT_DIR / 'src'
OUTPUT_DIR=PROYECT_DIR / 'output'
CHROMA_DIR=OUTPUT_DIR / 'chroma_db'
JSON=OUTPUT_DIR / "embeddings.json"
EXPORT_DIR=OUTPUT_DIR/ 'export'

# Constantes
TOP_K=3
CHUNK_SIZE=800
CHUNK_OVERLAP=100
MAX_GRUPO=175
MAX_GRUPO_CHROMA=500
MAX_CHUNK=100000
EMBEDDING_MODEL='gemini-embedding-001'
COLLECTION_NAME='InfoSport'
GEMINI_MODEL="gemini-3.1-flash-lite"
TEMPERATURE=0.2

#Instrucciones
RAG_BEHAVIOUR='''Eres un asistente sobre la competicion y los partidos de Madrid.

Reglas:
- Usa ÚNICAMENTE el contexto proporcionado.
- Responde SOLO con un JSON válido (sin markdown ni texto fuera del JSON).
- Esquema exacto:
  {
    "respuesta": string,
    "hay_evidencia": boolean,
    "fuentes_citadas": [string]
  }
- Si el contexto no basta, hay_evidencia=False y explica la abstención en respuesta.
- fuentes_citadas: nombres de archivo que aparecen en el contexto (si los hay).'''
