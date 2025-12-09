import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import subprocess
import sys

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.2,  # low temp = precise, consistent code
    streaming=True
)


def get_user_folder(user_id: str) -> str:
    #Get or create user-specific code folder.
    folder = os.path.join("outputs", user_id, "code")
    os.makedirs(folder, exist_ok=True)
    return folder