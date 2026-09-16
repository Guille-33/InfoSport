from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def create_chunks(*,docs:list[Document],c_size:int,c_overlap:int)->list[Document]:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=c_size,
        chunk_overlap=c_overlap
    )
    chunks=splitter.split_documents(docs)
    for i,c in enumerate(chunks):
        c.metadata['chunk_index']=i
    return chunks