import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import urllib.parse
import base64
import httpx
from openai import OpenAI

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