
from pathlib import Path
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from config import DATA_DIR, CSV_INSTALACIONES, EXTENSIONES_PDF, EXTENSIONES_TEXTO, EXTENSIONES_CSV


def fila_deporte_a_texto(fila) -> str:
    """Convierte una fila del CSV de polideportivos en un texto plano fácil de leer."""
    # Cojo los campos más típicos que suelen venir en un CSV municipal básico
    nombre = str(fila.get("nombre", fila.get("NOMBRE", "Instalación deportiva")))
    direc = str(fila.get("direccion", fila.get("DIRECCION", "Dirección no especificada")))
    barrio = str(fila.get("barrio", fila.get("BARRIO", "")))
    
    # Montando un texto simple con la info
    texto = f"Instalación municipal: {nombre}. Dirección: {direc}."
    if barrio:
        texto += f" Barrio o zona: {barrio}."
        
    return texto


def cargar_csv_deportes(ruta: Path) -> list[Document]:
    """Lee el CSV de instalaciones y crea un Document de LangChain por cada fila."""
    df = pd.read_csv(ruta, sep=";", encoding="utf-8")
    documentos = []

    for _, fila in df.iterrows():
        texto = fila_deporte_a_texto(fila)
        
        # para saber de qué archivo viene
        metadata = {
            "source": str(ruta.name),
            "tipo": "csv_instalacion"
        }
        
        documentos.append(Document(page_content=texto, metadata=metadata))

    return documentos


def cargar_archivo(ruta: Path) -> list[Document]:
    """Selecciona cómo abrir el archivo según su extensión."""
    sufijo = ruta.suffix.lower()

    # Si es PDF uso PyPDFLoader
    if sufijo in EXTENSIONES_PDF:
        return PyPDFLoader(str(ruta)).load()

    # Si es texto o markdown
    if sufijo in EXTENSIONES_TEXTO:
        return TextLoader(str(ruta), encoding="utf-8").load()

    # Si es el CSV de deportes
    if sufijo in EXTENSIONES_CSV:
        return cargar_csv_deportes(ruta)

    return []


def cargar_documentos() -> list[Document]:
    """Recorre la carpeta data/ y carga todos los archivos soportados."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"No encuentro la carpeta data en: {DATA_DIR}")

    documentos = []

    # Recorro todos los ficheros de la carpeta data
    for ruta in sorted(DATA_DIR.rglob("*")):
        if not ruta.is_file():
            continue
        if ruta.name == "README.md":
            continue

        docs = cargar_archivo(ruta)
        if docs:
            print(f"Cargado correctamente: {ruta.name} ({len(docs)} elementos)")
            documentos.extend(docs)

    return documentos