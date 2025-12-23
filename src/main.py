#FastAPI setup

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app - FastAPI(
    title="Broodmother API",
    description="Multi-agent AI system powered by LangGraph"
    version="1.0.0"
)