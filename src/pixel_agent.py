import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

# Pixel uses GPT-4 Vision for image analysis
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    streaming=True
)