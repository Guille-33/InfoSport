from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader,PyPDFLoader
import pandas as pd
import re 

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
            if e.lower()=='gratuito':
                v_str = str(v).split('.')[0] 
                if v_str=='0':
                    lineas.append(f'{e}: no')
                elif v_str=='1':
                    lineas.append(f'{e}: si')
                else:
                    lineas.append(f'{e}: unknown')
            else:
                lineas.append(f'{e}: {v}')
    return '\n'.join(lineas)

def nombre(file:Path)->str:
    division=file.stem.split('-')
    palabras=[p for p in division if not p.isdigit() and p.lower() not in {'csv','txt','pdf','xlsx'}]
    return '-'.join(palabras)

def corpus(data:Path)->list[Document]:
    docs:list[Document]=[]
    for file in data.iterdir():
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
            case '.csv':
                csv_df=pd.read_csv(file,sep=';',encoding='latin-1')
                etiquetas=csv_df.columns.tolist()
                for _, fila in csv_df.iterrows():
                    texto=fila_a_txt(fila,etiquetas)
                    if texto:
                        metadata={
                            'source':str(file),
                            'tipo': nombre(file)
                        }
                        docs.append(
                            Document(
                                page_content=texto,
                                metadata=metadata
                            )
                        )
        print (f' {file.name}: +{len(docs) - antes} documento(s)')
    return docs

def normalizar(text:str)->str:
    t=text.replace('\r\n','\n').replace('\r','\n')
    t=re.sub(r'\n{3.}','\n\n',t)
    t=re.sub(r'[ \t]+',' ',t)
    return '\n'.join(linea.strip() for linea in t.split('\n')).strip()
