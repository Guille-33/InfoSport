from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_OVERLAP,CHUNK_SIZE

def create_chunks(*,docs:list[Document],c_size:int|None=CHUNK_SIZE,c_overlap:int=CHUNK_OVERLAP)->list[Document]:
    if c_size is None:
        c_size=CHUNK_SIZE
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=max(c_size,CHUNK_SIZE),
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks=splitter.split_documents(docs)
    for i,c in enumerate(chunks):
        c.metadata['chunk_index']=i
    return chunks