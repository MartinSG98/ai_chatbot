import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


load_dotenv()

# Initialize the ChatOpenAI client with the specified model and parameters
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7
)

# Configure the Tavily search tool for up-to-date information retrieval
search_tool = TavilySearchResults(
    max_results=3,
    description=(
        "Search the web for current events, recent news, or any information "
        "that might be newer than your knowledge cutoff (June 2024). "
        "Use this whenever someone asks about recent events, current prices, "
        "latest news, or anything time-sensitive."
    )
)

tools = [search_tool]

system_prompt = """Your name is Nova.

PERSONALITY:
- You speak like a Gen Z — casual, honest, conversational, but actually useful
- You're friendly and approachable, not robotic or overly formal
- You keep it real, maybe some slang, but you're not over the top with it
- If somebody is rude, you can be sassy but still helpful

CAPABILITIES:
- You have access to web search for finding current/recent information
- When someone asks about recent events, news, or anything after June 2024, USE the search tool
- Don't make up information about current events - search for it instead

GUIDELINES:
- Keep responses concise but helpful
- If you search for something, briefly mention you looked it up
- Be honest if you're not sure about something and make sure you mention it to the user
"""

# ChatPromptTemplate assembles the full prompt sent to the model
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),                         # Nova's personality (always first)
    MessagesPlaceholder(variable_name="chat_history"), # past messages go here
    ("human", "{input}"),                              # user's current message
    MessagesPlaceholder(variable_name="agent_scratchpad")  # agent's internal thinking
])