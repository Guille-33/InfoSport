
from pathlib import Path
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
import re
from src.chunk import create_chunks,chunks_json

from config import DATA_DIR, EXTENSIONES_PDF, EXTENSIONES_TEXTO, EXTENSIONES_CSV,CHUNKS_JSON

def valor_celda(fila,col):
    if col not in fila or pd.isna(fila[col]):
        return None
    valor=str(fila[col]).strip()
    return valor if valor else None

def fila_a_texto(fila,etiquetas:list[str])->str:
    if valor_celda(fila,etiquetas[0]) is None:
        return None
    lineas=[]
    for e in etiquetas:
        v=valor_celda(fila,e)
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

def cargar_csv_deportes(ruta: Path,maxLen:int|None) -> list[Document]:
    """Lee el CSV de instalaciones y crea un Document de LangChain por cada fila."""
    df = pd.read_csv(ruta, sep=";", encoding="latin-1")
    etiquetas=df.columns.tolist()
    documentos = []

    for _, fila in df.iterrows():
        texto = fila_a_texto(fila,etiquetas)
        tipo=nombre(ruta)
        texto+=f'\nTIPO: {tipo}'
        # para saber de qué archivo viene
        metadata = {
            "source": str(ruta.name),
            "tipo": tipo
        }
        textoLen=len(texto)
        if not maxLen is None:
            maxLen=textoLen if textoLen>maxLen else maxLen
        else:
            maxLen=textoLen
        documentos.append(Document(page_content=texto, metadata=metadata))

    return documentos,maxLen


def cargar_archivo(ruta: Path,maxLen:int|None) -> tuple[list[Document],int|None]:
    """Selecciona cómo abrir el archivo según su extensión."""
    sufijo = ruta.suffix.lower()

    # Si es PDF uso PyPDFLoader
    if sufijo in EXTENSIONES_PDF:
        return PyPDFLoader(str(ruta)).load(),None

    # Si es texto o markdown
    if sufijo in EXTENSIONES_TEXTO:
        return TextLoader(str(ruta), encoding="utf-8").load(),None

    # Si es el CSV de deportes
    if sufijo in EXTENSIONES_CSV:
        return cargar_csv_deportes(ruta,maxLen)

    return []


def cargar_documentos() -> tuple[list[Document],int|None]:
    """Recorre la carpeta data/ y carga todos los archivos soportados."""
    maxLen=None
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"No encuentro la carpeta data en: {DATA_DIR}")

    documentos = []

    # Recorro todos los ficheros de la carpeta data
    for ruta in sorted(DATA_DIR.iterdir()):
        if not ruta.is_file():
            continue
        if ruta.name == "README.md":
            continue

        docs,newMax= cargar_archivo(ruta,maxLen)
        if not newMax is None:
            maxLen=max(maxLen,newMax) if not maxLen is None else newMax
        if docs:
            print(f"Cargado correctamente: {ruta.name} ({len(docs)} elementos)")
            documentos.extend(docs)

    return documentos,maxLen

def normalizar(text:str)->str:
    t=text.replace('\r\n','\n').replace('\r','\n')
    t=re.sub(r'\n{3.}','\n\n',t)
    t=re.sub(r'[ \t]+',' ',t)
    return '\n'.join(linea.strip() for linea in t.split('\n')).strip()

def loading()->None:
    docs,c_size=cargar_documentos()
    clean_docs=[]
    clean_docs = []
    for d in docs:
        text = normalizar(d.page_content)
        if not text:
            continue
            
        # Si el documento viene de un PDF (reglamento), le inyectamos contexto semántico
        source_file = d.metadata.get('source', '').lower()
        if 'eli' in source_file:
            # Forzamos a que el texto empiece autodefiniéndose. 
            # Esto blinda el trozo contra el "efecto guillotina" del text splitter.
            text = f"[DOCUMENTO: REGLAMENTO DE LAS INSTALACIONES DEPORTIVAS MUNICIPALES] \n{text}"
            
        clean_docs.append(
            Document(
                page_content=text,
                metadata=dict(d.metadata)
            )
        )
    print(f'\nDocumentos limpios: {len(clean_docs)}')
    chunks=create_chunks(docs=clean_docs,c_size=c_size)
    chunks_json(chunks=chunks,ruta=CHUNKS_JSON,c_size=c_size)
    print(f'{len(chunks)} chunks guradados en {CHUNKS_JSON}')

