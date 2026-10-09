from google import genai
from config import RAG_BEHAVIOUR,GEMINI_MODEL,TEMPERATURE
from pathlib import Path

def generar_respuesta(client:genai.Client,prompt:str)->tuple[str,str]:
    modelResp=client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={'temperature':TEMPERATURE}
        )
    return (modelResp.text or '').strip(),GEMINI_MODEL

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