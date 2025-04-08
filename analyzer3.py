import os
import openai
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_completion(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Calls the OpenAI API with the provided prompt and returns the analysis.
    """
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def build_prompt(text: str) -> str:
    """
    Constructs the prompt for the LLM instructing it to analyze the provided text
    for potential fraudulent or non-compliant behavior.
    """
    return f"""
You are a banking compliance and fraud detection expert. You are trained to detect and categorize potential fraudulent or non-compliant communications.
Analyze the text between the triple quotes below. Your task is to determine if the content indicates:
1. Potential fraudulent activity.
2. Non-compliance with banking regulations (such as KYC/AML, insider trading, money laundering, misrepresentation, etc).

For your output, provide the following:
- Summary of what the text is about.
- List of any red flags or concerning statements.
- Whether Fraud or Compliance violation is suspected (Yes/No).
- If yes, explain why and what rule or pattern it potentially violates.
- Also the output with which this communication can be tagged.
- Suggested next action (e.g. escalate to compliance team, request more info, no action needed).

Be thorough, unbiased, and consider the context of the financial or banking industry.

\"\"\"{text}\"\"\"
"""
