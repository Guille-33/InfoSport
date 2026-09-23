from pathlib import Path

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

#Configuración del Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

#Rutas de carpetas
PROYECT_DIR=Path(__file__).resolve().parent
DATA_DIR=PROYECT_DIR / 'data'
ENTREGABLES_DIR=PROYECT_DIR / 'entregables'
QUERIES_DIR=PROYECT_DIR / 'queries'
OUTPUT_DIR=PROYECT_DIR / 'output'
CHROMA_DIR=OUTPUT_DIR / 'chroma_db'
EMBEDDINGS_JSON = OUTPUT_DIR / "embeddings.json"
EXPORT_DIR=OUTPUT_DIR/ 'export'
CHUNKS_JSON=OUTPUT_DIR/ 'chunks.json'

# Configuración de Embeddings
EMBEDDING_MODEL = "gemini-embedding-001"
MAX_CHUNKS_EMBED = 50  # Le pongo un límite para no gastar ni tardar mucho probando
EMBED_BATCH_SIZE = 200

# Archivos del corpus de deportes

EXTENSIONES_TEXTO = {".txt", ".md"}
EXTENSIONES_PDF = {".pdf"}
EXTENSIONES_CSV = {".csv"}

# Configuracion retrieval

TOP_K=3
MAX_GRUPO_CHROMA=500
COLLECTION_NAME='InfoSport'
GEMINI_MODEL="gemini-3.1-flash-lite"
TEMPERATURE=0.2