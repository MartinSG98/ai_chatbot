import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from datetime import datetime

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    streaming=True
)

def get_user_folder(user_id: str) -> str:
    """Get or create user-specific output folder."""
    folder = os.path.join("outputs", user_id)
    os.makedirs(folder, exist_ok=True)  # S3 bucket later
    return folder


@tool
def create_document(user_id: str, filename: str, content: str) -> str:
    """
    Create a text document or file with the given content.
    
    Use this when someone asks to:
    - Write/create a document, note, or file
    - Save text to a file
    - Create a report, essay, letter, or any written content
    
    Args:
        user_id: The user's unique identifier
        filename: Name of the file (e.g., "notes.txt", "report.md", "letter.txt")
        content: The text content to write to the file
    """
    try:
        folder = get_user_folder(user_id)
        filepath = os.path.join(folder, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"✅ Document created: {filename}"
    except Exception as e:
        return f"Couldn't create document: {e}"


@tool
def read_document(user_id: str, filename: str) -> str:
    """
    Read and return the contents of a text file.
    
    Use this when someone asks to:
    - Read a file
    - Show contents of a document
    - Review what's in a file
    
    Args:
        user_id: The user's unique identifier
        filename: Name of the file to read
    """
    try:
        folder = get_user_folder(user_id)
        filepath = os.path.join(folder, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"📄 Contents of {filename}:\n\n{content}"
    except FileNotFoundError:
        return f"File not found: {filename}"
    except Exception as e:
        return f"Couldn't read file: {e}"


@tool
def list_documents(user_id: str) -> str:
    """
    List all documents for this user.
    
    Use this when someone asks:
    - What files exist
    - Show my documents
    - What have I created
    
    Args:
        user_id: The user's unique identifier
    """
    try:
        folder = get_user_folder(user_id)
        files = os.listdir(folder)
        
        if not files:
            return "📁 No documents yet. Ask me to create one!"
        
        file_list = "\n".join(f"  - {f}" for f in files)
        return f"📁 Your documents:\n{file_list}"
    except Exception as e:
        return f"Couldn't list documents: {e}"


# Scribe's toolkit
tools = [create_document, read_document, list_documents]