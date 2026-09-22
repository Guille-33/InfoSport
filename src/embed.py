import json
import time
from pathlib import Path

from google import genai
from google.genai import types

from config import (
    CHUNKS_JSON,
    EMBED_BATCH_SIZE,
    EMBEDDING_MODEL,
    EMBEDDINGS_JSON,
    MAX_CHUNKS_EMBED,
)


def _extraer_vector(embedding_obj) -> list[float]:
    """Extrae los valores del objeto que devuelve la API de Gemini."""
    if hasattr(embedding_obj, "values"):
        return list(embedding_obj.values)
    return list(embedding_obj)


def cargar_chunks_json() -> list[dict]:
    """Lee el archivo de chunks que generamos en la fase anterior."""
    if not CHUNKS_JSON.exists():
        raise FileNotFoundError(
            f"No encuentro el archivo {CHUNKS_JSON}. Ejecuta primero la ingesta."
        )
    data = json.loads(CHUNKS_JSON.read_text(encoding="utf-8"))
    return data.get("chunks", [])


def embeddear_textos(client: genai.Client, textos: list[str]) -> list[list[float]]:
    """Manda los textos a Gemini en pequeños lotes para que nos devuelva sus vectores."""
    if not textos:
        return []

    vectores = []

    for inicio in range(0, len(textos), EMBED_BATCH_SIZE):
        lote = textos[inicio : inicio + EMBED_BATCH_SIZE]

        # Preparo el formato que pide Google GenAI
        contents = [types.Content(parts=[types.Part(text=t)]) for t in lote]

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=contents,
        )

        lote_vectores = [_extraer_vector(emb) for emb in result.embeddings]
        vectores.extend(lote_vectores)

    return vectores


def ejecutar_embeddings() -> tuple[list[dict], Path]:
    """Función principal que coordina la creación de los embeddings y los guarda en un JSON."""
    # Conecto con el cliente de Gemini (es necesario la API key en el .env)
    client = genai.Client()

    chunks = cargar_chunks_json()
    total_disponibles = len(chunks)

    # Si puse un límite en config, recortamos la lista para probar rápido
    if MAX_CHUNKS_EMBED is not None:
        chunks = chunks[:MAX_CHUNKS_EMBED]

    textos = [c["text"] for c in chunks]

    print(f"Generando embeddings para {len(textos)} trozos de texto...")
    inicio = time.perf_counter()
    vectores = embeddear_textos(client, textos)
    tiempo_ms = (time.perf_counter() - inicio) * 1000
    print(f"¡Listo! Tramos procesados en {tiempo_ms:.0f} ms usando {EMBEDDING_MODEL}")

    # Junto cada texto con su vector numérico y su metadato correspondiente
    items = []
    for chunk, vector in zip(chunks, vectores):
        items.append(
            {
                "text": chunk["text"],
                "vector": vector,
                "metadata": chunk.get("metadata", {}),
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

    return items, EMBEDDINGS_JSON