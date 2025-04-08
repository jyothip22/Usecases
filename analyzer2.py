import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

def build_prompt(text: str) -> str:
    return f"""
    You are a banking compliance and fraud detection expert.

    Analyze the following communication and answer the following:

    - Summary of the content
    - Any red flags or concerning statements
    - Whether Fraud or Compliance violation is suspected (Yes/No)
    - Why and which rule it potentially violates
    - Suggested tag/category
    - Suggested next action

    Text to analyze:
    \"\"\"{text}\"\"\"
    """

def analyze_email_text(text: str, model="gpt-3.5-turbo") -> str:
    prompt = build_prompt(text)
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content
