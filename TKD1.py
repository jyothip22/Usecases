import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables if available.
_ = load_dotenv(find_dotenv())

# Set the custom API endpoint URL.
# Example: "https://your-custom-api.example.com/analyze"
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "https://your-custom-api.example.com/analyze")

def get_instructions() -> str:
    """
    Returns the fixed instruction string that tells the custom API what analysis to perform.
    You can modify these instructions as needed.
    """
    instructions = (
        "You are a banking compliance and fraud detection expert. "
        "Analyze the following email content for compliance issues, and provide: "
        "a summary, a list of red flags, whether there is evidence of fraud or non-compliance, "
        "and a suggested next action."
    )
    print(f"DEBUG: Instructions: {instructions}")
    return instructions

def invoke_custom_api(instruction: str, input_text: str) -> str:
    """
    Invokes the custom API endpoint by sending a JSON payload that contains
    separate keys for the instruction and the input text.
    
    The payload will be:
        {
            "instruction": <instruction string>,
            "input_text": <email body text>
        }
    
    The API is expected to return a plain text response.
    
    Args:
        instruction (str): The prompt or instruction to guide the analysis.
        input_text (str): The email text to analyze.
    
    Returns:
        str: The plain text response from the custom API.
    """
    payload = {
        "instruction": instruction,
        "input_text": input_text
    }
    print("DEBUG: Invoking custom API with payload:")
    print(f"DEBUG: {payload}")
    
    try:
        response = requests.post(CUSTOM_API_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print("ERROR invoking custom API:", e)
        raise e
    
    # Assuming the API returns a plain text response.
    result = response.text
    print(f"DEBUG: Received custom API response (first 100 chars): {result[:100]}...")
    return result
