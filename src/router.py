# Routes user messages to the appropriate specialist agent:
# - Nova: Web search, current events
# - Wolf: Wikipedia, knowledge, research
# - Sage: Math, calculations
# - Pixel: Image generation & analysis
# - Scribe: Documents, writing, files
# - Onyx: Code, programming

import os
import time
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

load_dotenv()

class RouterState(TypedDict):
    #Data that flows through our agent graph.
    user_message: str                # what the user said
    session_id: str                  # conversation session
    user_id: str                     # for file-based agents
    agent_name: str                  # which agent was chosen
    response: str                    # final response to user