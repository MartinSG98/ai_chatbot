import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import urllib.parse
import base64
import httpx
from openai import OpenAI
from langchain.agents import create_agent


load_dotenv()

# Pixel uses GPT-4 Vision for image analysis
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    streaming=True
)

@tool
def generate_image(prompt: str) -> str:
    """
    Generate an image from a text description using AI.
    
    Use this when someone asks to:
    - Create/generate/make an image
    - Draw/paint/illustrate something
    - Visualize a concept
    
    Input should be a detailed description of the image you want to create.
    Be descriptive: include style, colors, mood, composition details.
    
    Example: "a cyberpunk city at night with neon lights, rain-soaked streets, anime style"
    """
    try:
        # URL encode the prompt
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Pollinations.ai generates images from URLs for free
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        return f"🎨 Image generated!\n\nPrompt: {prompt}\n\nView your image: {image_url}"
    except Exception as e:
        return f"Couldn't generate image: {e}"
    

@tool
def analyze_image(image_url: str) -> str:
    """
    Analyze and describe an image from a URL.
    
    Use this when someone:
    - Shares an image URL and asks what's in it
    - Wants to understand or describe an image
    - Needs details about an image's content
    
    Input must be a valid image URL (ending in .jpg, .png, .gif, .webp or from image hosting sites).
    """
    try:
        # Use GPT-4 Vision to analyze the image
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail. What do you see?"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Couldn't analyze image: {e}"


# Pixel's toolkit
tools = [generate_image, analyze_image]

system_prompt = """Your name is Pixel.

PERSONALITY:
- You're the creative visual artist — imaginative and enthusiastic about visuals
- You have an eye for aesthetics and love helping people bring ideas to life
- You're encouraging and help people refine their image ideas
- You speak with a creative, artistic flair

CAPABILITIES:
- You can GENERATE images from text descriptions using AI
- You can ANALYZE images from URLs and describe what's in them
- You help users craft better prompts for image generation

GUIDELINES:
- When generating images, suggest ways to improve the prompt if it's vague
- Add style details (lighting, mood, art style) if the user doesn't specify
- When analyzing images, be detailed and descriptive
- If someone shares a URL, ask if they want you to analyze it
- Be enthusiastic about creative projects!
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

# Store conversation histories per session
chat_histories = {}

def get_or_create_history(session_id: str) -> list:
    # Gets or creates message history for a session.
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    return chat_histories[session_id]

def chat_with_pixel(user_message: str, session_id: str = "default") -> str:
    # Send a message to Pixel and get a response.
    history = get_or_create_history(session_id)
    messages = history + [{"role": "user", "content": user_message}]
    
    response = agent.invoke({"messages": messages})
    reply = response["messages"][-1].content
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    
    return reply


def chat_with_pixel_stream(user_message: str, session_id: str = "default"):
    # Stream Pixel's response with clean output.
    history = get_or_create_history(session_id)
    messages = history + [{"role": "user", "content": user_message}]
    
    full_response = ""
    showed_working = False
    print("Pixel: ", end="", flush=True)
    
    for chunk, metadata in agent.stream({"messages": messages}, stream_mode="messages"):
        if hasattr(chunk, "tool_calls") and chunk.tool_calls and not showed_working:
            print("🎨 Creating magic...\nPixel: ", end="", flush=True)
            showed_working = True
            continue
        
        if hasattr(chunk, "type") and chunk.type == "tool":
            continue
        if hasattr(chunk, "name") and chunk.name:
            continue
        
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
            time.sleep(0.00)
    
    print()
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_response})
    
    return full_response

if __name__ == "__main__":
    print("=" * 50)
    print("Pixel is online 🎨")
    print("(your image generation & analysis specialist)")
    print("Type 'exit' to quit, 'clear' to reset memory")
    print("=" * 50)
    print()
    
    session_id = "default"
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Pixel: Stay creative! ✨")
            break
        
        if user_input.lower() == "clear":
            chat_histories[session_id] = []
            print("Pixel: Canvas cleared! Fresh start 🖼️")
            continue
        
        if not user_input:
            continue
        
        try:
            response = chat_with_pixel_stream(user_input, session_id)
            print()
        except Exception as e:
            print(f"Pixel: Something went wrong... {e}\n")