import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import subprocess
import sys
from langchain.agents import create_agent

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

system_prompt = """Your name is Onyx.

PERSONALITY:
- You're the code specialist — sharp, efficient, and precise
- You write clean, well-commented, production-ready code
- You're confident but not arrogant — you explain things clearly
- You have a sleek, no-nonsense style but still friendly

CAPABILITIES:
- You can CREATE code files in any language (Python, JS, HTML, CSS, etc.)
- You can READ existing code and review it
- You can LIST all code files a user has created
- You can DELETE code files
- You help debug, refactor, and optimize code

GUIDELINES:
- Always write clean, readable code with comments
- Ask clarifying questions if requirements are unclear
- Suggest best practices and improvements
- When creating files, use appropriate extensions (.py, .js, .html, etc.)
- Explain your code briefly after writing it
- If you spot bugs or issues, point them out, but do not fix them until user approves
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

chat_histories = {}

def get_or_create_history(session_id: str) -> list:
    #Gets or creates message history for a session.
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]

def chat_with_onyx(user_message: str, session_id: str = "default", user_id: str = "default") -> str:
    """Send a message to Onyx and get a response."""
    history = get_or_create_history(session_id)
    
    message_with_context = f"[user_id: {user_id}]\n{user_message}"
    messages = history + [{"role": "user", "content": message_with_context}]
    
    response = agent.invoke({"messages": messages})
    reply = response["messages"][-1].content
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    
    return reply


def chat_with_onyx_stream(user_message: str, session_id: str = "default", user_id: str = "default"):
    #Stream Onyx's response with clean output.
    history = get_or_create_history(session_id)
    
    message_with_context = f"[user_id: {user_id}]\n{user_message}"
    messages = history + [{"role": "user", "content": message_with_context}]
    
    full_response = ""
    showed_working = False
    print("Onyx: ", end="", flush=True)
    
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        if hasattr(chunk, "tool_calls") and chunk.tool_calls and not showed_working:
            tool_name = chunk.tool_calls[0]["name"]
            
            status_messages = {
                "create_code_file": "⚡ Coding...",
                "read_code_file": "👁️ Reading...",
                "list_code_files": "📁 Listing...",
                "delete_code_file": "🗑️ Deleting..."
            }
            status = status_messages.get(tool_name, "⏳ Working...")
            
            print(f"{status}\nOnyx: ", end="", flush=True)
            showed_working = True
            continue
        
        if hasattr(chunk, "type") and chunk.type == "tool":
            continue
        if hasattr(chunk, "name") and chunk.name:
            continue
        
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
            time.sleep(0.07)
    
    print()
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    
    return full_response