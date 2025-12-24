#FastAPI setup
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from router import chat, last_agent_tracker
from database import save_message, get_chat_history, delete_chat_history
from rag_service import add_document, search_documents, delete_user_documents, DOCUMENTS_DIR
import shutil
import os

app = FastAPI(
    title="Broodmother API",
    description="Multi-agent AI system powered by LangGraph",
    version="1.0.0"
)

#Middleware to allow connection to frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # to be updated
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # will generate if not provided
    user_id: Optional[str] = None     # will come from auth later

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    session_id: str

class AgentInfo(BaseModel):
    name: str
    description: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):

    session_id = request.session_id or str(uuid4())
    user_id = request.user_id or "anonymous"

    try:
        # Save user message to db
        save_message(session_id, "user", request.message)
        # Send to Broodmother
        response = chat(request.message, session_id, user_id)
        # Get which agent was used
        agent_used = last_agent_tracker.get(session_id, "unknown")
        # Save assistant response to db
        save_message(session_id, "assistant", response, agent_name=agent_used)

        return ChatResponse(
            response=response,
            agent_used=agent_used,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents", response_model=list[AgentInfo])
def get_agents():

    agents = [
        AgentInfo(name="Nova", description="Web search and current events"),
        AgentInfo(name="Wolf", description="Wikipedia and knowledge research"),
        AgentInfo(name="Sage", description="Math and calculations"),
        AgentInfo(name="Pixel", description="Image generation and analysis"),
        AgentInfo(name="Scribe", description="Document creation and management"),
        AgentInfo(name="Onyx", description="Code generation and programming"),
    ]

    return agents

@app.get("/health")
def health_check():

    return {"status": "healthy", "service": "Broodmother API"}

@app.get("/history/{session_id}")
def get_history(session_id: str):

    messages = get_chat_history(session_id)
    return {"session_id": session_id, "messages": messages}

@app.delete("/history/{session_id}")
def delete_history(session_id: str):

    deleted_count = delete_chat_history(session_id)
    return {"session_id": session_id, "deleted": deleted_count}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = "default"):
    
    allowed_extenstions = [".pdf", ".docx", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extenstions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not support. Allowed: {allowed_extenstions}"
        )

    file_path = os.path.join(DOCUMENTS_DIR, f"{user_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks_added = add_document(file_path, user_id)
        return {
            "filename": file.filename,
            "user_id": user_id,
            "chunks_added": chunks_added,
            "message": "Document uploaded and indexed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/search")
def search_docs(query: str, user_id: str = "default", k: int = 3):

    results = search_documents(query, user_id, k)
    
    return {
        "query": query,
        "results": [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in results
        ]
    }

@app.delete("/documents/{user_id}")
def delete_docs(user_id:str):

    deleted_count = delete_user_documents(user_id)

    return{
        "user_id": user_id,
        "deleted_chunks": deleted_count
    }


@app.get("/sessions")
def get_sessions():
    from database import table
    
    response = table.scan(
        ProjectionExpression="session_id"
    )
    
    # Get unique session IDs
    session_ids = list(set(item["session_id"] for item in response.get("Items", [])))
    
    return {"sessions": session_ids}