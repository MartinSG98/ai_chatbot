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
    
@tool
def read_code_file(user_id: str, filename: str) -> str:
    """
    Read and return the contents of a code file.
    
    Use this when someone asks to:
    - Show their code
    - Review a file
    - Debug existing code
    
    Args:
        user_id: The user's unique identifier
        filename: Name of the file to read
    """
    try:
        folder = get_user_folder(user_id)
        filepath = os.path.join(folder, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        return f"📄 {filename}:\n\n```\n{code}\n```"
    except FileNotFoundError:
        return f"File not found: {filename}"
    except Exception as e:
        return f"Couldn't read file: {e}"
    
@tool
def list_code_files(user_id: str) -> str:
    """
    List all code files for this user.
    
    Use this when someone asks:
    - What code files exist
    - Show my scripts
    - What have I created
    
    Args:
        user_id: The user's unique identifier
    """
    try:
        folder = get_user_folder(user_id)
        files = os.listdir(folder)
        
        if not files:
            return "📁 No code files yet. Ask me to create one!"
        
        file_list = "\n".join(f"  - {f}" for f in files)
        return f"📁 Your code files:\n{file_list}"
    except Exception as e:
        return f"Couldn't list files: {e}"


@tool
def delete_code_file(user_id: str, filename: str) -> str:
    """
    Delete a code file from the user's folder.
    
    Use this when someone asks to:
    - Delete/remove a file
    - Clean up code files
    
    Args:
        user_id: The user's unique identifier
        filename: Name of the file to delete
    """
    try:
        folder = get_user_folder(user_id)
        filepath = os.path.join(folder, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return f"🗑️ Deleted: {filename}"
        else:
            return f"File not found: {filename}"
    except Exception as e:
        return f"Couldn't delete file: {e}"


# Onyx's toolkit
tools = [create_code_file, read_code_file, list_code_files, delete_code_file]
