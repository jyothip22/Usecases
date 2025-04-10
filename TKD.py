import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables if available.
_ = load_dotenv(find_dotenv())

# Set the custom API endpoint URL.
# Example: "https://your-custom-api.example.com/analyze"
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "https://your-custom-api.example.com/analyze")

def build_prompt(text: str) -> str:
    """
    Constructs an analysis prompt from the given email content.
    
    For example, you might want to instruct the API to analyze the email for compliance issues.
    The prompt here is kept simple; you can modify the text as needed.
    
    Args:
        text (str): The formatted email body.
    
    Returns:
        str: The prompt string.
    """
    prompt = f"Analyze the following email content for compliance issues:\n{text}"
    print(f"DEBUG: Built prompt (first 100 chars): {prompt[:100]}...")
    return prompt

def invoke_custom_api(prompt: str, param1: str = "", param2: str = "") -> str:
    """
    Invokes a custom API endpoint by sending a JSON payload.
    
    The payload includes the prompt and additional string parameters.
    The custom API is expected to return a plain text response.
    
    Args:
        prompt (str): The analysis prompt.
        param1 (str): Custom parameter 1 (as string).
        param2 (str): Custom parameter 2 (as string).
    
    Returns:
        str: The response from the custom API.
    """
    payload = {
        "prompt": prompt,
        "param1": param1,
        "param2": param2
    }
    print("DEBUG: Invoking custom API with payload:", payload)
    
    try:
        response = requests.post(CUSTOM_API_URL, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes.
    except Exception as e:
        print("ERROR invoking custom API:", e)
        raise e
    
    # Assuming the API returns a plain text response.
    result = response.text
    print(f"DEBUG: Received custom API response (first 100 chars): {result[:100]}...")
    return result
