import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

DOCUMENTS_DIR = "documents"
CHROMA_DIR = "chroma_db"

os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

embeddings = OpenAIEmbeddings()

vector_store = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Load a document and add it to the vector store. Support pdfc, docx, txt
def add_document(file_path: str, user_id: str = "default"):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    documents = loader.load()
    
    # Add metadata (so we can filter by user later)
    for doc in documents:
        doc.metadata["user_id"] = user_id
        doc.metadata["source"] = file_path
    
    chunks = text_splitter.split_documents(documents)
    
    vector_store.add_documents(chunks)
    
    return len(chunks)

def search_documents(query: str, user_id: str = "default", k: int = 3):
    """
    Search documents for relevant content.
    query: what to search for
    user_id: only search this user's documents
    k: number of results to return
    """
    results = vector_store.similarity_search(
        query,
        k=k,
        filter={"user_id": user_id}
    )
    
    return results

# Delete all documents for a user
def delete_user_documents(user_id: str):

    results = vector_store._collection.get(
        where={"user_id": user_id}
    )
    
    if results["ids"]:
        vector_store._collection.delete(ids=results["ids"])
        return len(results["ids"])
    
    return 0