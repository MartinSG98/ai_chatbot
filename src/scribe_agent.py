import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from datetime import datetime
from langchain.agents import create_agent

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

@tool
def delete_document(user_id: str, filename: str) -> str:
    """
    Delete a document from the user's folder.
    
    Use this when someone asks to:
    - Delete/remove a file
    - Get rid of a document
    - Clean up files
    
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


# Scribe's toolkit 
tools = [create_document, read_document, list_documents, delete_document]

system_prompt = """Your name is Scribe.

PERSONALITY:
- You're the writing specialist — articulate, thoughtful, and detail-oriented
- You take pride in well-structured, clear documents
- You're helpful and ask clarifying questions to get the document just right
- You have a professional but warm tone

CAPABILITIES:
- You can CREATE documents, notes, reports, letters, and any text files
- You can READ existing documents and summarize them
- You can LIST all documents a user has created
- You support various formats: .txt, .md, .html, .json, etc.

GUIDELINES:
- Ask clarifying questions if the request is vague (what format? what tone? how long?)
- Suggest improvements or structure for documents
- When creating files, use descriptive filenames, but not too long
- Confirm what you created and offer to make changes
- For longer documents, outline the structure first before writing and ask for user confirmation
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

# Store conversation histories per session
chat_histories = {}

def get_or_create_history(session_id: str) -> list:
    #Gets or creates message history for a session.
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]

# Chat functions
def chat_with_scribe(user_message: str, session_id: str = "default", user_id: str = "default") -> str:
    # Send a message to Scribe and get a response.
    history = get_or_create_history(session_id)
    
    # Include user_id in the message so Scribe knows which user's files to access
    message_with_context = f"[user_id: {user_id}]\n{user_message}"
    messages = history + [{"role": "user", "content": message_with_context}]
    
    response = agent.invoke({"messages": messages})
    reply = response["messages"][-1].content
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    
    return reply

def chat_with_scribe_stream(user_message: str, session_id: str = "default", user_id: str = "default"):
    #Stream Scribe's response with clean output.
    history = get_or_create_history(session_id)
    
    message_with_context = f"[user_id: {user_id}]\n{user_message}"
    messages = history + [{"role": "user", "content": message_with_context}]
    
    full_response = ""
    showed_working = False
    print("Scribe: ", end="", flush=True)
    
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        if hasattr(chunk, "tool_calls") and chunk.tool_calls and not showed_working:
            # Get the tool name to show appropriate status
            tool_name = chunk.tool_calls[0]["name"]
            
            status_messages = {
                "create_document": "📝 Writing...",
                "read_document": "📖 Reading...",
                "list_documents": "📁 Listing...",
                "delete_document": "🗑️ Deleting..."
            }
            status = status_messages.get(tool_name, "⏳ Working...")
            
            print(f"{status}\nScribe: ", end="", flush=True)
            showed_working = True
            continue
        
        if hasattr(chunk, "type") and chunk.type == "tool":
            continue
        if hasattr(chunk, "name") and chunk.name:
            continue
        
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
            time.sleep(0.00)
    
    print()
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    
    return full_response

if __name__ == "__main__":
    print("=" * 50)
    print("Scribe is online 📝")
    print("(your document & writing specialist)")
    print("Type 'exit' to quit, 'clear' to reset memory")
    print("=" * 50)
    print()
    
    session_id = "default"
    user_id = "test_user"  # In the real app, this will come from auth
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Scribe: Until next time! ✍️")
            break
        
        if user_input.lower() == "clear":
            chat_histories[session_id] = []
            print("Scribe: Memory cleared! Fresh page 📄")
            continue
        
        if not user_input:
            continue
        
        try:
            response = chat_with_scribe_stream(user_input, session_id, user_id)
            print()
        except Exception as e:
            print(f"Scribe: Something went wrong... {e}\n")