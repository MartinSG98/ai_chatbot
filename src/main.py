#FastAPI setup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from router import chat, last_agent_tracker
from database import save_message, get_chat_history, delete_chat_history

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