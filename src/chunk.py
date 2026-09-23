from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_OVERLAP,CHUNK_SIZE,CHUNKS_JSON
from pathlib import Path
import json

def create_chunks(*,docs:list[Document],c_size:int|None=CHUNK_SIZE,c_overlap:int=CHUNK_OVERLAP)->list[Document]:
    if c_size is None:
        c_size=CHUNK_SIZE
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=max(c_size,CHUNK_SIZE),
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks=splitter.split_documents(docs)
    for i,c in enumerate(chunks):
        c.metadata['chunk_index']=i
    return chunks

def documents_2_dicts(documentos: list[Document]) -> list[dict]:
    return [
        {"text": doc.page_content, "metadata": dict(doc.metadata)}
        for doc in documentos
    ]

def chunks_json(chunks: list[Document], ruta: Path,c_size:int|None=CHUNK_SIZE) -> None:
    if c_size is None:
        c_size=CHUNK_SIZE
    ruta.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "chunk_size_config": {
            "chunk_size": c_size,
            "chunk_overlap": CHUNK_OVERLAP,
        },
        "total_chunks": len(chunks),
        "chunks": documents_2_dicts(chunks),
    }

    ruta.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def cargar_chunks() -> list[dict]:
    if not CHUNKS_JSON.exists():
        raise FileNotFoundError(
            f"No existe {CHUNKS_JSON}. Ejecuta antes: python main.py --prepare"
        )
    data = json.loads(CHUNKS_JSON.read_text(encoding="utf-8"))
    return data.get("chunks", [])