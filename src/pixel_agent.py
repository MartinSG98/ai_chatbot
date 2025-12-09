import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import urllib.parse
import base64
import httpx


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