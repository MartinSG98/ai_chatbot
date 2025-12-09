import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

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