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
from nova_agent import chat_with_nova_stream
from wolf_agent import chat_with_wolf_stream
from sage_agent import chat_with_sage_stream
from pixel_agent import chat_with_pixel_stream
from scribe_agent import chat_with_scribe_stream
from onyx_agent import chat_with_onyx_stream


load_dotenv()

class RouterState(TypedDict):
    # Data that flows through our agent graph.
    user_message: str                # what the user said
    session_id: str                  # conversation session
    user_id: str                     # for file-based agents
    agent_name: str                  # which agent was chosen
    response: str                    # final response to user


# Broodmother's brain (low temp = consistent decisions)
broodmother_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

def broodmother_classify(state: RouterState) -> RouterState:
    """
    The Broodmother analyzes the message and assigns it to the right agent.
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

    response = broodmother_llm.invoke(classification_prompt)
    agent_name = response.content.strip().lower()
    
    # Validate - default to nova if unclear
    valid_agents = ["nova", "wolf", "sage", "pixel", "scribe", "onyx"]
    if agent_name not in valid_agents:
        agent_name = "nova"
    
    state["agent_name"] = agent_name
    return state

# Define each agent node in the graph
def nova_node(state: RouterState) -> RouterState:
    response = chat_with_nova_stream(state["user_message"], state["session_id"])
    state["response"] = response
    return state

def wolf_node(state: RouterState) -> RouterState:
    response = chat_with_wolf_stream(state["user_message"], state["session_id"])
    state["response"] = response
    return state

def sage_node(state: RouterState) -> RouterState:
    response = chat_with_sage_stream(state["user_message"], state["session_id"])
    state["response"] = response
    return state

def pixel_node(state: RouterState) -> RouterState:
    response = chat_with_pixel_stream(state["user_message"], state["session_id"])
    state["response"] = response
    return state

def scribe_node(state: RouterState) -> RouterState:
    response = chat_with_scribe_stream(state["user_message"], state["session_id"], state["user_id"])
    state["response"] = response
    return state

def onyx_node(state: RouterState) -> RouterState:
    response = chat_with_onyx_stream(state["user_message"], state["session_id"], state["user_id"])
    state["response"] = response
    return state

# Return the name of the agent node to route to.
def route_to_agent(state: RouterState) -> str:
    return state["agent_name"]


# Create the graph
graph = StateGraph(RouterState)

# Add nodes
graph.add_node("broodmother", broodmother_classify)
graph.add_node("nova", nova_node)
graph.add_node("wolf", wolf_node)
graph.add_node("sage", sage_node)
graph.add_node("pixel", pixel_node)
graph.add_node("scribe", scribe_node)
graph.add_node("onyx", onyx_node)

# Connect: START → broodmother
graph.add_edge(START, "broodmother")

# Conditional routing: broodmother → appropriate agent
graph.add_conditional_edges(
    "broodmother",
    route_to_agent,
    {
        "nova": "nova",
        "wolf": "wolf",
        "sage": "sage",
        "pixel": "pixel",
        "scribe": "scribe",
        "onyx": "onyx"
    }
)

# All agents → END
graph.add_edge("nova", END)
graph.add_edge("wolf", END)
graph.add_edge("sage", END)
graph.add_edge("pixel", END)
graph.add_edge("scribe", END)
graph.add_edge("onyx", END)

# Compile the graph
colony = graph.compile()