from src.retrieve import search_k,json_2_datos,generar_context,generar_respuesta,build_prompt
import chromadb
import json
from src.google_authen import create_client
from src.index import create_chroma
from config import TOP_K

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

def responder(*,pregunta:str,top_k:int|None=TOP_K)->dict:
    if top_k is None:
        top_k=TOP_K
    client=create_client()
    question=(pregunta or "").strip()
    if not question:
        return{
            "respuesta": "",
            "contexto": "",
            "results": None,
            "fuentes": [],
            "error": "La pregunta no puede estar vacía.",
        }
    resultados=search_k(pregunta=question,top_k=top_k)
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
    