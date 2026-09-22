from pathlib import Path

#Configuración del Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

#Rutas de carpetas
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
CHUNKS_JSON = OUTPUT_DIR / "chunks.json"
EMBEDDINGS_JSON = OUTPUT_DIR / "embeddings.json"

# Configuración de Embeddings
EMBEDDING_MODEL = "gemini-embedding-2"
MAX_CHUNKS_EMBED = 50  # Le pongo un límite para no gastar ni tardar mucho probando
EMBED_BATCH_SIZE = 50

# Archivos del corpus de deportes
CSV_INSTALACIONES = "200186-0-polideportivos-csv.csv"  # CSV que voy a usar de instalaciones deportivas

EXTENSIONES_TEXTO = {".txt", ".md"}
EXTENSIONES_PDF = {".pdf"}
EXTENSIONES_CSV = {".csv"}