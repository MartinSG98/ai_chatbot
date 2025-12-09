import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize the ChatOpenAI client with the specified model and parameters
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7
)