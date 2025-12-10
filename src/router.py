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
    user_message: str
    session_id: str
    user_id: str
    agent_name: str
    response: str
    last_agent_used: str


# Broodmother's brain (low temp = consistent decisions)
broodmother_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

def broodmother_classify(state: RouterState) -> dict:
    """
    The Broodmother analyzes the message and assigns it to the right agent.
    Returns only the fields being updated.
    """
    user_message = state["user_message"].lower()
    last_agent_used = state.get("last_agent_used", "") or ""
    
    # If it looks like a follow-up, use last agent
    follow_up_phrases = [
        "delete it", "remove it", "delete that", "remove that",
        "show it", "show me", "edit it", "change it", "update it",
        "can you delete", "can you remove", "now delete", "now remove",
        "thanks", "thank you", "ok now", "okay now", "great now",
        "the file", "that file", "this file"
    ]
    
    if last_agent_used and any(phrase in user_message for phrase in follow_up_phrases):
        return {
            "agent_name": last_agent_used,
            "last_agent_used": last_agent_used
        }
    
    # Otherwise, ask the LLM to classify
    classification_prompt = f"""Analyze this message and decide which agent should handle it.

AGENTS:
- nova: Web search, current events, news, real-time info, anything needing internet
- wolf: Wikipedia, facts, history, definitions, general knowledge, research
- sage: Math, calculations, numbers, equations, percentages
- pixel: Images - generating, creating, analyzing, describing pictures
- scribe: Documents, notes, writing files, creating text files, summaries
- onyx: Code, programming, scripts, debugging, any coding language

USER MESSAGE: {state["user_message"]}

Respond with ONLY the agent name (nova/wolf/sage/pixel/scribe/onyx), nothing else."""

    response = broodmother_llm.invoke(classification_prompt)
    agent_name = response.content.strip().lower()
    
    valid_agents = ["nova", "wolf", "sage", "pixel", "scribe", "onyx"]
    if agent_name not in valid_agents:
        agent_name = "nova"
    
    return {
        "agent_name": agent_name,
        "last_agent_used": agent_name
    }


# Define each agent node in the graph - return only updated fields
def nova_node(state: RouterState) -> dict:
    response = chat_with_nova_stream(state["user_message"], state["session_id"])
    return {"response": response}

def wolf_node(state: RouterState) -> dict:
    response = chat_with_wolf_stream(state["user_message"], state["session_id"])
    return {"response": response}

def sage_node(state: RouterState) -> dict:
    response = chat_with_sage_stream(state["user_message"], state["session_id"])
    return {"response": response}

def pixel_node(state: RouterState) -> dict:
    response = chat_with_pixel_stream(state["user_message"], state["session_id"])
    return {"response": response}

def scribe_node(state: RouterState) -> dict:
    response = chat_with_scribe_stream(state["user_message"], state["session_id"], state["user_id"])
    return {"response": response}

def onyx_node(state: RouterState) -> dict:
    response = chat_with_onyx_stream(state["user_message"], state["session_id"], state["user_id"])
    return {"response": response}


# Return the name of the agent node to route to
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

# Track last agent across calls
last_agent_tracker = {}

def chat(user_message: str, session_id: str = "default", user_id: str = "default") -> str:
    """
    Send a message to the Broodmother and get a response from the right agent.
    """
    # Get last agent for this session
    last_agent = last_agent_tracker.get(session_id, "")
    
    result = colony.invoke({
        "user_message": user_message,
        "session_id": session_id,
        "user_id": user_id,
        "agent_name": "",
        "response": "",
        "last_agent_used": last_agent
    })
    
    # Save the agent that was used for next time
    last_agent_tracker[session_id] = result["last_agent_used"]
    
    return result["response"]


if __name__ == "__main__":
    print("=" * 50)
    print("🕷️ Broodmother is online")
    print("Routing to: Nova | Wolf | Sage | Pixel | Scribe | Onyx")
    print("Type 'exit' to quit")
    print("=" * 50)
    print()
    
    session_id = "default"
    user_id = "test_user"
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("🕷️ Broodmother: The colony rests... for now.")
            break
        
        if not user_input:
            continue
        
        try:
            response = chat(user_input, session_id, user_id)
            print()
        except Exception as e:
            print(f"🕷️ Broodmother: Something went wrong... {e}\n")