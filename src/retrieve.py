from pathlib import Path
import chromadb
from langchain_core.documents import Document
from src.embed import embed_question
from google import genai
from config import TOP_K,RAG_BEHAVIOUR,GEMINI_MODEL,TEMPERATURE
import re,json

def search_k(*,client:genai.Client,collection:chromadb.Collection,pregunta:str):
    vecPregunta=embed_question(client=client,question=pregunta)
    totalCollection=collection.count()
    try:
        resultados=collection.query(
            query_embeddings=vecPregunta,
            n_results=min(totalCollection,TOP_K),
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

def resp_ok(datos:dict,context,resultados)->dict:
    evidencia=datos.get('hay_evidencia',False)
    respuesta=datos.get('respuesta','')
    fuentes=datos.get('fuentes_citadas',[])
    if evidencia:
        print(f'''
RESPUESTA [OK]
-------------------

{respuesta}

---- EVIDENCIAS ---
{"\n- ".join([f"- {f}" for f in fuentes])}
''')
    else:
        print(f'''
RESPUESTA [Not Found]
-------------------

Motivo: {respuesta}
Para más información visite https://www.madrid.es/portales/munimadrid/es/Inicio/Cultura-ocio-y-deporte/Deportes?vgnextfmt=default&vgnextchannel=c7a8efff228fe410VgnVCM2000000c205a0aRCRD
''')
    return {
        "respuesta": respuesta,
        "contexto": context,
        "results": resultados,
        "fuentes": fuentes,
        "error": '',
    }
def resp_error(respuesta,error):
    print(f'''
REPUESTA [ERROR]
-------------------

La respuesta no se ha generado correctamente, si el error persiste contacte con los creadores
''')
    return{
        "respuesta": respuesta,
        "contexto": '',
        "results": '',
        "fuentes": [],
        "error": error,
    }

def generar_respuesta(client:genai.Client,prompt:str)->str:
    modelResp=client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={'temperature':TEMPERATURE}
        )
    return (modelResp.text or '').strip()

def responder(*,pregunta:str,client:genai.Client,collection:chromadb.Collection)->dict:
    question=(pregunta or "").strip()
    if not question:
        return{
            "respuesta": "",
            "contexto": "",
            "results": None,
            "fuentes": [],
            "error": "La pregunta no puede estar vacía.",
        }
    resultados=search_k(client=client,collection=collection,pregunta=question)
    context=generar_context(resultados=resultados)
    if context == "Fuera de scope":
        return {
            "respuesta": "",
            "contexto": context,
            "results": resultados,
            "fuentes": [],
            "error": "No se recuperó contexto. Revisa el índice.",
        }
    prompt=build_prompt(context=context,pregunta=question)
    modelResp=generar_respuesta(client=client,prompt=prompt)
    try:
        datos=json_2_datos(modelResp)
        return resp_ok(datos=datos,context=context,resultados=resultados)
    except json.JSONDecodeError as e:
        error=str(e)
        return resp_error(respuesta=modelResp,error=error)
