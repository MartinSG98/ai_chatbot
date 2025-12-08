from openai import OpenAI
import config

client = OpenAI(api_key=config.openai_api_key)

def generate_text(prompt, model="gpt-4.1-mini", max_tokens=150):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content

prompt = "Explain the theory of relativity in simple terms."
result = generate_text(prompt)
print(result)
