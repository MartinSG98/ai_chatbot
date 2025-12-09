import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool  
import numexpr


load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.1,  
    streaming=True
)

@tool
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations. Use this for ANY math-related question.
    
    ALWAYS convert word problems to expressions before calculating:
    - "what is 15% of 200" → "200 * 0.15"
    - "5 squared" → "5 ** 2"
    - "square root of 16" → "16 ** 0.5"
    - "20 divided by 4" → "20 / 4"
    
    Supported operations:
    - Basic: +, -, *, /
    - Powers: ** (e.g., 2**3 = 8)
    - Parentheses: (2 + 3) * 4
    - Decimals: 3.14 * 2
    
    Input must be a valid math expression, NOT words.
    """
    try:
        expr = expression.replace("^", "**")
        result = numexpr.evaluate(expr).item()
        return f"{result}"
    except Exception as e:
        return f"Couldn't calculate: {e}"
    
# Sage's toolkit
tools = [calculator]