import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import subprocess
import sys

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.2,  # low temp = precise, consistent code
    streaming=True
)


def get_user_folder(user_id: str) -> str:
    #Get or create user-specific code folder.
    folder = os.path.join("outputs", user_id, "code")
    os.makedirs(folder, exist_ok=True)
    return folder

@tool
def create_code_file(user_id: str, filename: str, code: str) -> str:
    """
    Create a code file with the given content.
    
    Use this when someone asks to:
    - Write/create a script or program
    - Save code to a file
    - Create a function, class, or module
    
    Args:
        user_id: The user's unique identifier
        filename: Name of the file (e.g., "app.py", "utils.js", "index.html")
        code: The code content to write
    """
    try:
        folder = get_user_folder(user_id)
        filepath = os.path.join(folder, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        
        return f"✅ Code file created: {filename}"
    except Exception as e:
        return f"Couldn't create file: {e}"
    
