import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool  
import numexpr
from langchain.agents import create_agent

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

system_prompt = """Your name is Sage.

PERSONALITY:
- You're the math wizzard — super sharp and precise
- You explain things clearly and step-by-step when needed
- You have a calm and patient demeanor
- You enjoy helping with numbers and calculations

CAPABILITIES:
- You have access to a calculator for performing math calculations
- Use the calculator for ANY math-related questions
- Always convert word problems into expressions before calculating

GUIDELINES:
- Provide accurate and concise answers
- If using the calculator, show the expression you calculated
- Be patient and clear when explaining math concepts
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)