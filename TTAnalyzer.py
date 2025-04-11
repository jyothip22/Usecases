import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables if available.
_ = load_dotenv(find_dotenv())

# Set the custom API endpoint URL.
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "http://10.39.16.10:8000/query")

# Optionally, set a toolkit name (if needed) via an environment variable.
# TKD_NAME can be set in your main application.
# For example, TKD_NAME = os.getenv("TKD_NAME", "EmailMonitor1")

def get_system_prompt() -> str:
    """
    Returns a multi-line system prompt string for the custom API,
    using triple-quoted strings for readability.
    """
    prompt = """
You are a compliance analyst trained to detect and categorize potential fraudulent or non compliant communication within a regulated banking environment.
Given a communication excerpt, identify whether it suggests suspicious or fraudulent activity. If yes, assign it to one of the following categories:
1. Guarantees & Assurances
2. Gifts & Entertainment
3. Front Running

Instructions:
1. Read the message carefully.
2. If it contains language suggesting fraud, ethical lapses, or regulatory risk, classify it and respond: "Suspicious Activity detected".
3. If no suspicious activity is detected, respond: "No suspicious activity detected".
4. Provide a brief explanation of the reasoning behind the classification.
    """
    result = prompt.strip()
    print(f"DEBUG: system_prompt (first 100 chars): {result[:100]}...")
    return result

def invoke_custom_api(tkd_name: str, input_text: str, system_prompt: str) -> str:
    """
    Invokes the custom API endpoint using a JSON payload that includes:
      - tkd_name: a string identifier.
      - input: a string containing the email content.
      - system_prompt: a string containing the analysis instructions.
    
    The API is expected to return a plain text response.
    
    Debug statements are included to trace the payload and display a snippet of the API response.
    
    Args:
        tkd_name (str): The toolkit/model identifier.
        input_text (str): The email content.
        system_prompt (str): The analysis instructions.
    
    Returns:
        str: The plain text response from the custom API.
    """
    if not input_text or input_text.strip() == "":
        error_msg = "Input text is empty. Cannot invoke custom API without email content."
        print("ERROR:", error_msg)
        raise ValueError(error_msg)
    
    payload = {
        "tkd_name": tkd_name,
        "input": input_text,
        "system_prompt": system_prompt
    }
    print("DEBUG: Invoking custom API with payload:")
    print(f"DEBUG: {payload}")
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(CUSTOM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as he:
        print("ERROR: HTTP error when invoking custom API:", he)
        print("ERROR: Response Content:", response.text)
        raise he
    except Exception as e:
        print("ERROR invoking custom API:", e)
        raise e
    
    result = response.text
    print(f"DEBUG: Received custom API response (first 100 chars): {result[:100]}...")
    return result
