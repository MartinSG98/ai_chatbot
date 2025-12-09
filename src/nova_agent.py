import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent  
import time

load_dotenv()

# Initialize the ChatOpenAI client with the specified model and parameters
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    streaming=True
)

# Configure the Tavily search tool for up-to-date information retrieval
search_tool = TavilySearch(
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

# NEW: create_agent is much simpler - just pass model, tools, and system_prompt
# No need for ChatPromptTemplate, AgentExecutor, or agent_scratchpad anymore
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

# Store conversation histories per session
chat_histories = {}

def get_or_create_history(session_id: str) -> list:
    """Gets or creates message history for a session."""
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]

#Send a message to Nova and get a response.
def chat_with_nova(user_message: str, session_id: str = "default") -> str:
    # Get this session's history
    history = get_or_create_history(session_id)
    
    # Build messages: history + current message
    messages = history + [{"role": "user", "content": user_message}]
    
    # Invoke the agent
    response = agent.invoke({"messages": messages})
    
    # Extract the reply (last message from the agent)
    reply = response["messages"][-1].content
    
    # Save to history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    
    return reply

def chat_with_nova_stream(user_message: str, session_id: str = "default"):
    
    #Stream Nova's response token by token. 
    history = get_or_create_history(session_id)
    messages = history + [{"role": "user", "content": user_message}]
    
    full_response = ""
    showed_searching = False
    print("Nova: ", end="", flush=True)
    
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        # Check if this is a tool call (searching)
        if hasattr(chunk, "tool_calls") and chunk.tool_calls and not showed_searching:
            print("🔍 Searching...\nNova: ", end="", flush=True)
            showed_searching = True
            continue
        
        # Skip tool responses (the raw JSON)
        if hasattr(chunk, "type") and chunk.type == "tool":
            continue
            
        # Skip if chunk is tool output (has name attribute = tool name)
        if hasattr(chunk, "name") and chunk.name:
            continue
        
        # Only print actual assistant content
        if hasattr(chunk, "content") and chunk.content:
            # Skip if content looks like JSON tool output
            if chunk.content.strip().startswith('{"query"'):
                continue
                
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
            time.sleep(0.07)
    
    print()  # New line after finishing response
    
    # Save to history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    
    return full_response

# MAIN LOOP (for testing in terminal)
if __name__ == "__main__":
    print("=" * 50)
    print("Nova is online 😎")
    print("(now with web search powers)")
    print("Type 'exit' to quit, 'clear' to reset memory")
    print("=" * 50)
    print()
    
    session_id = "default"
    
    while True:
        user_input = input("You: ").strip()
        
        # Exit commands
        if user_input.lower() in ["exit", "quit", "bye", "cya", "goodbye"]:
            print("Nova: Catch you later! ✨")
            break
        
        # Clear memory
        if user_input.lower() == "clear":
            chat_histories[session_id] = []
            print("Nova: Memory cleared! Fresh start 🧹")
            continue
        
        # Skip empty input
        if not user_input:
            continue
        
        # Get response from Nova
        try:
            response = chat_with_nova_stream(user_input, session_id)
            print()  # extra line for spacing
        except Exception as e:
            print(f"Nova: Something broke... {e}\n")