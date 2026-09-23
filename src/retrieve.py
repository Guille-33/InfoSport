from pathlib import Path
import chromadb
from langchain_core.documents import Document
from src.embed import embed_question
from google import genai
from config import RAG_BEHAVIOUR,GEMINI_MODEL,TEMPERATURE,TOP_K
import re,json
from src.index import create_chroma
from src.google_authen import create_client

def search_k(*,pregunta:str,top_k:int|None):
    if top_k is None:
        top_k=TOP_K
    client=create_client
    collection=create_chroma(create=False)
    vecPregunta=embed_question(client=client,question=pregunta)
    totalCollection=collection.count()
    try:
        resultados=collection.query(
            query_embeddings=vecPregunta,
            n_results=min(totalCollection,top_k),
            include=['documents','metadatas','distances']
        )
        return resultados
    except Exception as e:
        print ('Error:',e)
        return None

def generar_context(resultados:dict)->str:
    ids=resultados['ids'][0]
    documents=resultados['documents'][0]
    metadatas=resultados['metadatas'][0]
    distances=resultados['distances'][0]
    lines=[]
    for i,doc_id in enumerate(ids):
        text=documents[i]
        dist=distances[i]
        meta=metadatas[i]
        ruta=Path(meta.get('source','?')).name
        lines.append(f'''
--- Fragmento {i+1} (distancia={dist:.4f}) ---
Fuente: {ruta}
{text}
''')
    if not lines:
        return 'Fuera de scope'
    return '\n\n'.join(lines)

def build_prompt(context:str,pregunta:str)->str:
    return(
        f"{RAG_BEHAVIOUR.strip()}\n\n"
        f"--- CONTEXTO RECUPERADO ---\n"
        f"{context.strip()}\n\n"
        f"--- PREGUNTA ---\n"
        f"{pregunta.strip()}\n\n"
        f"--- JSON ---"
    )

def json_2_datos(respuesta:str)->dict:
    text=respuesta
    if text.startswith("```"):
        text=re.sub(r'^```(?:json)\s*','',text)
        text=re.sub(r'\s*```$','',text)
    return json.loads(text)

def generar_respuesta(client:genai.Client,prompt:str)->str:
    modelResp=client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={'temperature':TEMPERATURE}
        )
    return (modelResp.text or '').strip()