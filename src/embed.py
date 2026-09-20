from google import genai
from google.genai import types
from langchain_core.documents import Document
from pathlib import Path
import json
import time
import joblib
from config import EMBEDDING_MODEL,MAX_CHUNK,MAX_GRUPO,EXPORT_DIR,JSON

def embedding(texts:list[str],client:genai.Client)->list[list[float]]:
    if not texts:
        return []
    contents=[]
    for t in texts:
        contents.append(types.Content(parts=[types.Part(text=t)]))
    result=client.models.embed_content(model=EMBEDDING_MODEL,contents=contents)
    v=[]
    for e in result.embeddings:
        v.append(list(e.values))
    return v

def embed_batch(texts:list[str]):
    LenSet=len(texts)
    for i in range (0,LenSet,MAX_GRUPO):
        siguiente=min(i+MAX_GRUPO,LenSet)
        yield texts[i:siguiente]


def embed_chunks(*,client:genai.Client,chunks:list[Document])->list[dict]:
    vectores=[]
    if MAX_CHUNK is None:
        subset=chunks
    else:
        subset=chunks[:MAX_CHUNK]
    texts=[]
    for c in subset:
        texts.append(c.page_content)
    # vectores=embedding(texts=texts,client=client,model=model)
    for batch_texto in embed_batch(texts=texts):
        n_vectores=embedding(texts=batch_texto,client=client)
        vectores.extend(n_vectores)
        print(f'{len(vectores)}/{len(subset)}')
        time.sleep(0.2)
    items=[]
    for c,v in zip (subset,vectores):
        items.append({
            'text':c.page_content,
            'vector':v,
            'metadata':dict(c.metadata)
        })

    # payload={
    #     'embedding_model':model,
    #     'total':len(items),
    #     'chunks':len(chunks),
    #     'dimensions':len(vectores[0]) if vectores else 0,
    #     'items':items
    # }
    # json_dir.write_text(
    #     json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8'
    # )
    try:
        EXPORT_DIR.mkdir(parents=True,exist_ok=True)
        numeroArchivo=1+sum(1 for x in EXPORT_DIR.iterdir() if x.is_file())
        nombreArchivo=f'embedding_chunk_{numeroArchivo}'
        archivo_dir=EXPORT_DIR / nombreArchivo
        joblib.dump(items,archivo_dir,compress=3)
    except Exception as e:
        print ('Error:',e)
    return items

def embed_question(client:genai.Client,question:str)->list[float]:
    contents=[types.Content(parts=[types.Part(text=question.strip())])]
    response=client.models.embed_content(model=EMBEDDING_MODEL,contents=contents)
    return list(response.embeddings[0].values)

def create_json(items:list[dict]):
    itemsLen=len(items)
    dimension=len(items[0]['vector']) if items else 0
    JSON.parent.mkdir(parents=True,exist_ok=True)

    with open(JSON,'w',encoding='utf-8') as j:
        j.write("{\n")
        j.write(f'  "embedding_model": "{EMBEDDING_MODEL}",\n')
        j.write(f'  "total": {itemsLen},\n')
        j.write(f'  "dimensions": {dimension},\n')
        j.write('  "items": [\n')
        for i,item in enumerate(items):
            item_dump=json.dumps(item,ensure_ascii=False,indent=2)
            lineas_indentadas = []
            for linea in item_dump.splitlines():
                lineas_indentadas.append(f"    {linea}")
            item_formateado = "\n".join(lineas_indentadas)
            j.write(item_formateado)
            if i < itemsLen - 1:
                j.write(",\n")
            else:
                j.write("\n")
        j.write('  ]\n}')
