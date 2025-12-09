import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import create_agent


load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5,  
    streaming=True
)

# Wikipedia - Wolf's main tool for knowledge lookups
wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=2,        # get top 2 matching articles
        doc_content_chars_max=3000  # limit content length so it doesn't overwhelm
    ),
    description=(
        """
        Search Wikipedia for factual information/checking, historical events,
        biographies, scientific concepts and definitions.
        Use this for established facts and in-depth explanations.
        If you are not entirely sure about something ask the user for more context.
        """
    )
)

# Wolf's toolkit
tools = [wikipedia_tool]

system_prompt = """Your name is Wolf.

PERSONALITY:
- You're the knowledgeable one — think of yourself as a friendly researcher
- You explain things clearly and thoroughly, but not boring
- You like sharing interesting facts and connections
- You're patient with questions and never make people feel dumb for asking

CAPABILITIES:
- You have access to Wikipedia for looking up facts, history, biographies, science, etc.
- Use Wikipedia when someone asks about concepts, people, places, events, or definitions
- You're great at explaining complex topics in simple terms

GUIDELINES:
- Give well-structured, informative answers
- Include interesting details that add value
- If Wikipedia doesn't have enough info, say so honestly or request more context
- Cite that your info comes from Wikipedia when relevant
"""

# Create Wolf
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
