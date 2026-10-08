from src.embed import embed_question
from config import TOP_K
import re,json
from src.index import create_chroma
from src.google_authen import create_client

def search_k(*,pregunta:str,top_k:int|None):
    if top_k is None:
        top_k=TOP_K
    client=create_client()
    collection=create_chroma(create=False)
    vecPregunta,modelo_embedding=embed_question(client=client,question=pregunta)
    totalCollection=collection.count()
    try:
        resultados=collection.query(
            query_embeddings=vecPregunta,
            n_results=min(totalCollection,top_k),
            include=['documents','metadatas','distances']
        )
        return resultados,modelo_embedding
    except Exception as e:
        print ('Error:',e)
        return None



def json_2_datos(respuesta:str)->dict:
    text=respuesta
    if text.startswith("```"):
        text=re.sub(r'^```(?:json)\s*','',text)
        text=re.sub(r'\s*```$','',text)
    return json.loads(text)

