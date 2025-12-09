import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

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