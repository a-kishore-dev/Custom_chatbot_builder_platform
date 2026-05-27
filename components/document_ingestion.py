from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from streamlit import session_state as ss

def load_documents_into_vectordb(file, db_name):
    document = PyMuPDFLoader(file).load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    final_document = text_splitter.split_documents(document)
    if not ss.chats[ss.current_chat].get("vector_store"):
        vector_store = Chroma(
            collection_name=db_name,
            embedding_function=embedding,
            persist_directory=f"./chroma_db/{db_name}"
        )
        ss.chats[ss.current_chat]["vector_store"] = vector_store
    else:
        vector_store = ss.chats[ss.current_chat]["vector_store"]
    vector_store.add_documents(final_document)
