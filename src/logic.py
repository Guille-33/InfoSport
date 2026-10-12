from src.retrieve import search_k,json_2_datos
from src.generate import generar_context,generar_respuesta,build_prompt
import json
from src.google_authen import create_client
from src.logging_utils import registrar_consulta_json
from config import TOP_K,MAX_QUEST
import time

def resp_ok(datos:dict,context,resultados)->tuple[str,dict]:
    evidencia=datos.get('hay_evidencia',False)
    respuesta=datos.get('respuesta','')
    fuentes=datos.get('fuentes_citadas',[])
    if evidencia:
        texto=f'''
RESPUESTA [OK]
-------------------

{respuesta}

---- EVIDENCIAS ---
{"\n- ".join([f"- {f}" for f in fuentes])}
'''
    else:
        texto=f'''
RESPUESTA [Not Found]
-------------------

Motivo: {respuesta}
Para más información visite https://www.madrid.es/portales/munimadrid/es/Inicio/Cultura-ocio-y-deporte/Deportes?vgnextfmt=default&vgnextchannel=c7a8efff228fe410VgnVCM2000000c205a0aRCRD
'''
    return texto, {
        "respuesta": respuesta,
        "contexto": context,
        "results": resultados,
        "fuentes": fuentes,
        "error": '',
    }
def resp_error(error,*,respuesta:str|None=None,contexto:str|None=None,results=None)->tuple[str,dict]:
    texto=f'''
REPUESTA [ERROR]
-------------------

La respuesta no se ha generado correctamente, si el error persiste contacte con los creadores

Error: {error}
'''
    return texto, {
        "respuesta": respuesta,
        "contexto": contexto,
        "results": results,
        "fuentes": [],
        "error": error,
    }

def responder(*,pregunta:str,top_k:int|None=TOP_K)->tuple[str,dict]:
    t_inicio=time.time()
    if top_k is None:
        top_k=TOP_K
    client=create_client()
    question=(pregunta or "").strip()
    if not question:
        return resp_error('La pregunta no puede estar vacía')
    elif len(pregunta)>MAX_QUEST:
        return resp_error('La pregunta es demasiado larga')
    resultados,modelo_embedding=search_k(pregunta=question,top_k=top_k)
    context=generar_context(resultados=resultados)
    if context == "Fuera de scope":
        return resp_error('No de recuperó contexto. Revisa el índice',contexto=context,results=resultados)
    prompt=build_prompt(context=context,pregunta=question)
    try:
        modelResp,modelo=generar_respuesta(client=client,prompt=prompt)
    except Exception as e:
        error=str(e)
        return resp_error(respuesta='',error=error)
    try:
        datos=json_2_datos(modelResp)
        se_abstuvo=not datos.get('hay_evidencia',False)
        num_chunks=len(resultados['documents'])
        t_ejec=time.time()-t_inicio
        registrar_consulta_json(pregunta=pregunta,k=top_k,num_chunks=num_chunks,tiempo_ejecucion=t_ejec,modelo=modelo,modelo_embedding=modelo_embedding,se_abstuvo=se_abstuvo)
        return resp_ok(datos=datos,context=context,resultados=resultados)
    except json.JSONDecodeError as e:
        error=str(e)
        return resp_error(error,respuesta=modelResp)

def rag_ask(pregunta:str,top_k:int|None)->str:
    texto,diccionario=responder(pregunta=pregunta,top_k=top_k)
    return texto
    
    