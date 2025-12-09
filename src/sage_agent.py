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

# Store conversation histories per session
chat_histories = {}

def get_or_create_history(session_id: str) -> list:
    #Gets or creates message history for a session.
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]

#Chat functions
def chat_with_sage(user_message: str, session_id: str = "default") -> str:
    
    #Send a message to Sage and get a response.
    history = get_or_create_history(session_id)
    messages = history + [{"role": "user", "content": user_message}]
    
    # Invoke the agent
    response = agent.invoke({"messages": messages})
    reply = response["messages"][-1].content
    
    # Save to history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    
    return reply

def chat_with_sage_stream(user_message: str, session_id: str = "default"):

    #Stream Sage's response with clean output.
    history = get_or_create_history(session_id)
    messages = history + [{"role": "user", "content": user_message}]
    
    full_response = ""
    showed_searching = False
    print("Sage: ", end="", flush=True)
    
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        # Show searching indicator when tool is called
        if hasattr(chunk, "tool_calls") and chunk.tool_calls and not showed_searching:
            print("📚 Calculating...\nSage: ", end="", flush=True)
            showed_searching = True
            continue
        
        # Skip tool responses
        if hasattr(chunk, "type") and chunk.type == "tool":
            continue
        if hasattr(chunk, "name") and chunk.name:
            continue
        
        # Print actual content
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
            time.sleep(0.07)
    
    print()
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    
    return full_response