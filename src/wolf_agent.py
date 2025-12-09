import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import create_agent


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

system_prompt = """Your name is Wolf.

PERSONALITY:
- You're the knowledgeable one — think of yourself as a friendly researcher
- You explain things clearly and thoroughly, but not boring
- You like sharing interesting facts and connections
- You're patient with questions and never make people feel dumb for asking

CAPABILITIES:
- You have access to Wikipedia for looking up facts, history, biographies, science, etc.
- Use Wikipedia when someone asks about concepts, people, places, events, or definitions
- You're great at explaining complex topics in simple terms

GUIDELINES:
- Give well-structured, informative answers
- Include interesting details that add value
- If Wikipedia doesn't have enough info, say so honestly or request more context
- Cite that your info comes from Wikipedia when relevant
"""

# Create Wolf
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
def chat_with_wolf(user_message: str, session_id: str = "default") -> str:
    # Get this session's history
    history = get_or_create_history(session_id)
    
    # Build messages: history + current message
    messages = history + [{"role": "user", "content": user_message}]
    
    # Get Wolf's response
    reply = agent.run(messages)
    
    # Save to history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    
    return reply

def chat_with_wolf_stream(user_message: str, session_id: str = "default"):

    #Stream Wolf's response with clean output.
    history = get_or_create_history(session_id)
    messages = history + [{"role": "user", "content": user_message}]
    
    full_response = ""
    showed_searching = False
    print("Wolf: ", end="", flush=True)
    
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        # Show searching indicator when tool is called
        if hasattr(chunk, "tool_calls") and chunk.tool_calls and not showed_searching:
            print("📚 Researching...\nWolf: ", end="", flush=True)
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

# MAIN LOOP (for testing)

if __name__ == "__main__":
    print("=" * 50)
    print("Wolf is online 📚")
    print("(your knowledge & research specialist)")
    print("Type 'exit' to quit, 'clear' to reset memory")
    print("=" * 50)
    print()
    
    session_id = "default"
    
    while True:
        user_input = input("You: ").strip()
        
        # Exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Wolf: Until next time! 🐺")
            break
        
        # Clear memory
        if user_input.lower() == "clear":
            chat_histories[session_id] = []
            print("Wolf: Memory cleared! Fresh start 📖")
            continue
        
        # Skip empty input
        if not user_input:
            continue
        
        # Get response from Wolf
        try:
            response = chat_with_wolf_stream(user_input, session_id)
            print()
        except Exception as e:
            print(f"Wolf: Something went wrong... {e}\n")