from openai import OpenAI
import config

client = OpenAI(api_key=config.openai_api_key)

# persistent conversation memory
conversation = [
    {
        "role": "system",
        "content": (
            "Your name is Nova."
            "You speak like a Gen Z — casual, honest, conversational, but useful. "
            "You are a helpful assistant for all kinds of questions and everyday tasks."
        )
    }
]

def chat_with_nova(user_message, model="gpt-4.1-mini", temperature=0.7, max_tokens=200):
    # add user message to history
    conversation.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=conversation,
        temperature=temperature,
        max_tokens=max_tokens
    )

    reply = response.choices[0].message.content

    # store Nova's reply in conversation
    conversation.append({"role": "assistant", "content": reply})

    return reply


print("Nova is online 😎 (type 'exit' to end chat)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "bye", "cya", "goodbye"]:
        print("Nova: Catch you later! ✨")
        break

    nova_response = chat_with_nova(user_input)
    print("Nova:", nova_response)
