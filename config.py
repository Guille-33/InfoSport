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

# Constantes

CHUNK_SIZE=800
CHUNK_OVERLAP=100
MAX_CHUNK=20
EMBEDDING_MODEL='gemini-embedding-2'
COLLECTION_NAME='InfoSport'
