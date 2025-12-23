import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

DOCUMENTS_DIR = "documents"
CHROMA_DIR = "chroma_db"

os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)