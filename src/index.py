import chromadb
from pathlib import Path
from langchain_core.documents import Document
from config import CHROMA_DIR,COLLECTION_NAME,MAX_GRUPO_CHROMA

def create_chroma()->chromadb.Collection:
    client=chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f'{COLLECTION_NAME} previa eliminada')
    except Exception:
        print(f'no hay {COLLECTION_NAME} previa')

    collection=client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

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

def index_2_chroma(items:list[Document])->chromadb.Collection:
    try:
        collection=create_chroma()
    except Exception as e:
        print('there was an error in chroma creation\n\nError:',str(e))
    for batch_items in index_batch(items=items):
        ids=[]
        embeddings=[]
        documents=[]
        metadatas=[]
        for i,item in enumerate(batch_items):
            metadata=sanitizar(item["metadata"])
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
        return collection
