import json
import time
import joblib
from pathlib import Path

from google import genai
from google.genai import types
from src.chunk import create_chunks
from langchain_core.documents import Document

from config import (
    EMBED_BATCH_SIZE,
    EMBEDDING_MODEL,
    EMBEDDINGS_JSON,
    MAX_CHUNKS_EMBED,
    EXPORT_DIR
)


def _extraer_vector(embedding_obj) -> list[float]:
    """Extrae los valores del objeto que devuelve la API de Gemini."""
    if hasattr(embedding_obj, "values"):
        return list(embedding_obj.values)
    return list(embedding_obj)


def embeddear_textos(client: genai.Client, textos: list[str]) -> list[list[float]]:
    """Manda los textos a Gemini en pequeños lotes para que nos devuelva sus vectores."""
    if not textos:
        return []

    vectores = []
    textosLen=len(textos)
    for inicio in range(0, textosLen, EMBED_BATCH_SIZE):
        siguiente=min(inicio+EMBED_BATCH_SIZE,textosLen)
        lote = textos[inicio : siguiente]
        # Preparo el formato que pide Google GenAI
        contents = [types.Content(parts=[types.Part(text=t)]) for t in lote]

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=contents,
        )

        lote_vectores = [_extraer_vector(emb) for emb in result.embeddings]
        vectores.extend(lote_vectores)
        print(f'{len(vectores)}/{textosLen}')

    return vectores

def embed_question(client:genai.Client,question:str)->list[float]:
    contents=[types.Content(parts=[types.Part(text=question.strip())])]
    response=client.models.embed_content(model=EMBEDDING_MODEL,contents=contents)
    return list(response.embeddings[0].values)

def ejecutar_embeddings(*,client:genai.Client,docs:list[Document],max_embed:int|None=MAX_CHUNKS_EMBED,c_size:int|None) -> tuple[list[dict], Path]:
    """Función principal que coordina la creación de los embeddings y los guarda en un JSON."""
    # Conecto con el cliente de Gemini (es necesario la API key en el .env)

    chunks = create_chunks(docs=docs,c_size=c_size)
    total_disponibles = len(chunks)

    # Si puse un límite en config, recortamos la lista para probar rápido
    if max_embed is not None:
        subset = chunks[:max_embed]
    else:
        subset=chunks

    textos = [c.page_content for c in subset]

    print(f"Generando embeddings para {len(textos)} trozos de texto...")
    inicio = time.perf_counter()
    vectores = embeddear_textos(client, textos)
    tiempo_ms = (time.perf_counter() - inicio) * 1000
    print(f"¡Listo! Tramos procesados en {tiempo_ms:.0f} ms usando {EMBEDDING_MODEL}")

    # Junto cada texto con su vector numérico y su metadato correspondiente
    items = []
    for chunk, vector in zip(subset, vectores):
        items.append(
            {
                "text": chunk.page_content,
                "vector": vector,
                "metadata": dict(chunk.metadata),
            }
        )

    # Preparo el resultado final para guardarlo
    payload = {
        "embedding_model": EMBEDDING_MODEL,
        "total": len(items),
        "dimensions": len(vectores[0]) if vectores else 0,
        "items": items,
    }

    # Creo la carpeta output si no existe y guardo el archivo
    EMBEDDINGS_JSON.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Guardado archivo de embeddings en: {EMBEDDINGS_JSON}")
    try:
        EXPORT_DIR.mkdir(parents=True,exist_ok=True)
        numeroArchivo=1+sum(1 for x in EXPORT_DIR.iterdir() if x.is_file())
        nombreArchivo=f'embedding_chunk_{numeroArchivo}'
        archivo_dir=EXPORT_DIR / nombreArchivo
        joblib.dump(items,archivo_dir,compress=3)
    except Exception as e:
        print ('Error:',e)

    return items, EMBEDDINGS_JSON
