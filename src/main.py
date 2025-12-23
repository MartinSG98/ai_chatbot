#FastAPI setup

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from router import chat, last_agent_tracker

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
def chat_endpoint(request: ChatRequest)

    session_id = request.session_id or str(uuid4())
    user_id = request.user_id or "anonymous"

    try:
        response = chat(request.message, session_id, user_id)
        agent_used = last_agent_tracker.get(session_id, "unknown")

        return ChatResponse(
            response=response,
            agent_used=agent_used,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))