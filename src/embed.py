from google import genai
from google.genai import types
from langchain_core.documents import Document
from pathlib import Path
import json

def embedding(texts:list[str],client:genai.Client,model:str)->list[list[float]]:
    if not texts:
        return []
    contents=[]
    for t in texts:
        contents.append(types.Content(parts=[types.Part(text=t)]))
    result=client.models.embed_content(model=model,contents=contents)
    v=[]
    for e in result.embeddings:
        v.append(list(e.values))
    return v

def embed_chunks(client:genai.Client,model:str,json_dir:Path,chunks:list[Document],max_c:int=None)->list[dict]:
    if max_c is None:
        subset=chunks
    else:
        subset=chunks[:max_c]
    texts=[]
    for c in subset:
        texts.append(c.page_content)
    vectores=embedding(texts=texts,client=client,model=model)
    items=[]
    for c,v in zip (subset,vectores):
        items.append({
            'text':c.page_content,
            'vector':v,
            'metadata':dict(c.metadata)
        })

    payload={
        'embedding_model':model,
        'total':len(items),
        'chunks':len(chunks),
        'dimensions':len(vectores[0]) if vectores else 0,
        'items':items
    }
    json_dir.write_text(
        json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8'
    )