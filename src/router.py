# Broodmother - routes user messages to the appropriate specialist agent:
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
from langchain_openai import ChatOpenAI


load_dotenv()

class RouterState(TypedDict):
    #Data that flows through our agent graph.
    user_message: str                # what the user said
    session_id: str                  # conversation session
    user_id: str                     # for file-based agents
    agent_name: str                  # which agent was chosen
    response: str                    # final response to user


# Broodmother's brain (low temp = consistent decisions)
classifier_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

def classify_message(state: RouterState) -> RouterState:
    """
    You are the Broodmother of our agents colony. You analyze the message from the user and assign it to the right agent.
    """
    user_message = state["user_message"]
    
    classification_prompt = f"""Analyze this message and decide which agent should handle it.

AGENTS:
- nova: Web search, current events, news, real-time info, anything needing internet
- wolf: Wikipedia, facts, history, definitions, general knowledge, research
- sage: Math, calculations, numbers, equations, percentages
- pixel: Images - generating, creating, analyzing, describing pictures
- scribe: Documents, notes, writing files, creating text files, summaries
- onyx: Code, programming, scripts, debugging, any coding language

USER MESSAGE: {user_message}

Respond with ONLY the agent name (nova/wolf/sage/pixel/scribe/onyx), nothing else."""

    response = classifier_llm.invoke(classification_prompt)
    agent_name = response.content.strip().lower()
    
    # Validate - default to nova if unclear
    valid_agents = ["nova", "wolf", "sage", "pixel", "scribe", "onyx"]
    if agent_name not in valid_agents:
        agent_name = "nova"
    
    state["agent_name"] = agent_name
    return state