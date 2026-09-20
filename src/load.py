from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader,PyPDFLoader
import pandas as pd
import re 
from src.chunk import create_chunks
from config import DATA_DIR

def valor_celda(fila,col):
    if col not in fila or pd.isna(fila[col]):
        return None
    valor=str(fila[col]).strip()
    return valor if valor else None

def fila_a_txt(fila,etiquetas:list[str]):
    if valor_celda(fila,etiquetas[0]) is None:
        return None
    lineas=[]
    for e in etiquetas:
        v=valor_celda(fila,e)
        if v:
            match e.lower():
                case 'estado':
                    match v:
                        case 'A':
                            vInterpretado='Reprogramado'
                        case 'C':
                            vInterpretado='Comite disciplinario'
                        case 'F':
                            vInterpretado='Finalizado'
                        case 'S':
                            vInterpretado='Suspendido'
                        case 'N':
                            vInterpretado='No presentado'
                        case 'O':
                            vInterpretado='Aplazado organizacion'
                        case 'R':
                            vInterpretado='Resultado desconocido'
                        case _:
                            vInterpretado='Desconocido'
                case 'sistema_competicion':
                    try:
                        vInterpretado=str(v)
                    except Exception:
                        vInterpretado='Error'
                case _:
                    vInterpretado=v
            lineas.append(f'{e}: {vInterpretado}')
    return '\n'.join(lineas)

def nombre(file:Path)->str:
    division=file.stem.split('-')
    palabras=[p for p in division if not p.isdigit() and p.lower() not in {'csv','txt','pdf','xlsx'}]
    return '-'.join(palabras)

def corpus()->tuple[list[Document],list[Document],list[Document]]:
    docs:list[Document]=[]
    maxLen=0
    for file in DATA_DIR.iterdir():
        if not file.is_file():
            continue
        antes=len(docs)
        suf=file.suffix.lower()
        match suf:
            case '.txt'|'.md':
                docs.extend(TextLoader(str(file),encoding='utf-8').load())
            case '.pdf':
                docs.extend(PyPDFLoader(str(file)).load())
            case '.xlsx':
                excel_df = pd.read_excel(file)
                etiquetas = excel_df.columns.tolist()
                for _, fila in excel_df.iterrows():
                    texto = fila_a_txt(fila, etiquetas)
                    if texto:
                        metadata = {
                            'source':str(file),
                            'tipo': nombre(file)
                            }
                        docs.append(
                            Document(
                                page_content=texto,
                                metadata=metadata
                                )
                            )
                        textoLen=len(texto)
                        maxLen=textoLen if textoLen>maxLen else maxLen
            case '.csv':
                csv_df=pd.read_csv(file,sep=';',encoding='latin-1')
                etiquetas=csv_df.columns.tolist()
                for _, fila in csv_df.iterrows():
                    texto=fila_a_txt(fila,etiquetas)
                    tipo=nombre(file)
                    texto+=f'\nTIPO: {tipo}'
                    if texto:
                        metadata={
                            'source':str(file),
                            'tipo': tipo
                        }
                        docs.append(
                            Document(
                                page_content=texto,
                                metadata=metadata
                            )
                        )
                        textoLen=len(texto)
                        maxLen=textoLen if textoLen>maxLen else maxLen
        print (f' {file.name}: +{len(docs) - antes} documento(s)')
    limpios = []
    for d in docs:
        texto_limpio = normalizar(d.page_content)
        if not texto_limpio:
            continue  
        limpios.append(
            Document(
                page_content=texto_limpio,
                metadata=dict(d.metadata), 
            )
        )
    chunks=create_chunks(docs=limpios,c_size=maxLen)
    return docs,limpios,chunks

def normalizar(text:str)->str:
    t=text.replace('\r\n','\n').replace('\r','\n')
    t=re.sub(r'\n{3.}','\n\n',t)
    t=re.sub(r'[ \t]+',' ',t)
    return '\n'.join(linea.strip() for linea in t.split('\n')).strip()
