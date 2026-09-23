import chromadb
from pathlib import Path
from langchain_core.documents import Document
from config import CHROMA_DIR,COLLECTION_NAME,MAX_GRUPO_CHROMA,EMBEDDINGS_JSON,EMBEDDING_MODEL
import json

def create_chroma(*,create:bool)->chromadb.Collection:
    client=chromadb.PersistentClient(path=str(CHROMA_DIR))
    if create:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f'{COLLECTION_NAME} previa eliminada')
        except Exception:
            print(f'no hay {COLLECTION_NAME} previa')

        collection=client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    else:
        collection=client.get_collection(COLLECTION_NAME)
    print(f'{collection.name} lista')
    return collection

def sanitizar(metadata:dict)->dict:
    clean={}
    for c,v in metadata.items():
        if v is None:
            continue
        clean[c]=v if isinstance(v,(str,int,float,bool)) else str(v)
    return clean

def index_batch(items:list[Document]):
    LenSet=len(items)
    for i in range (0,LenSet,MAX_GRUPO_CHROMA):
        siguiente=min(i+MAX_GRUPO_CHROMA,LenSet)
        yield items[i:siguiente]

def index_2_chroma(create:bool)->None:
    items,model=cargar_embeddings()
    try:
        collection=create_chroma(create=create)
    except Exception as e:
        print('there was an error in chroma creation\n\nError:',str(e))
    for batch_items in index_batch(items=items):
        ids=[]
        embeddings=[]
        documents=[]
        metadatas=[]
        for i,item in enumerate(batch_items):
            metadata=sanitizar(item["metadata"])
            metadata['embedding_model']=model
            index=metadata.get('chunk_index',i)

            ids.append(f'chunk_{index}')
            embeddings.append(item["vector"])
            documents.append(item["text"])
            metadatas.append(metadata)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    print (f'{collection.count()} indexado(s) en {collection.name}')

def cargar_embeddings() -> tuple[list[dict], str]:
    """Lee embeddings.json y devuelve (items, nombre del modelo usado).

    Cada item suele tener: text, vector, metadata.
    El modelo se guarda en metadatos del índice para documentar con qué
    embedding se construyó (debe coincidir con el de la consulta en Fase 2).
    """
    if not EMBEDDINGS_JSON.exists():
        raise FileNotFoundError(
            f"No existe {EMBEDDINGS_JSON}. Ejecuta antes: python main.py --prepare"
        )
    data = json.loads(EMBEDDINGS_JSON.read_text(encoding="utf-8"))
    modelo = data.get("embedding_model", EMBEDDING_MODEL)
    return data.get("items", []), modelo
