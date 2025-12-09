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

@tool
def create_document(filename: str, content: str) -> str:
    """
    Create a text document or file with the given content.
    
    Use this when someone asks to:
    - Write/create a document, note, or file
    - Save text to a file
    - Create a report, essay, letter, or any written content
    
    Args:
        filename: Name of the file (e.g., "notes.txt", "report.md", "letter.txt")
        content: The text content to write to the file
    """
    try:
        # Create outputs folder if it doesn't exist
        os.makedirs("outputs", exist_ok=True)
        
        filepath = os.path.join("outputs", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"✅ Document created: {filepath}"
    except Exception as e:
        return f"Couldn't create document: {e}"
    
@tool
def read_document(filepath: str) -> str:
    """
    Read and return the contents of a text file.
    
    Use this when someone asks to:
    - Read a file
    - Show contents of a document
    - Review what's in a file
    
    Args:
        filepath: Path to the file to read
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"📄 Contents of {filepath}:\n\n{content}"
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Couldn't read file: {e}"