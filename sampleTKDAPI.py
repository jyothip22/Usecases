import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables if available.
_ = load_dotenv(find_dotenv())

# Set the custom API endpoint URL.
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "https://your-custom-api.example.com/analyze")

def get_instructions() -> str:
    """
    Returns a multi-line instruction string for the custom API.
    
    Using triple-quoted strings allows us to maintain a clean, readable
    multi-line instruction without having to concatenate individual lines.
    """
    instructions = """
You are a banking compliance and fraud detection expert.
Analyze the following email content for compliance issues, and provide:
- A summary of the email content,
- A list of red flags,
- Whether there is evidence of fraud or non-compliance,
- A suggested next action.
    """
    # .strip() removes any leading/trailing whitespace/newlines.
    result = instructions.strip()
    print(f"DEBUG: Instructions (first 100 chars): {result[:100]}...")
    return result

def invoke_custom_api(instruction: str, input_text: str) -> str:
    """
    Invokes the custom API endpoint by sending a JSON payload with two keys:
      - 'instruction': a string that contains the prompt or instructions.
      - 'input_text': a string containing the email content to analyze.
    
    Since the custom API returns a plain text response, this function extracts
    the response text and returns it.
    
    Debug statements are added to trace the payload and to display a snippet of
    the received response.
    
    Args:
        instruction (str): The analysis instructions.
        input_text (str): The formatted email body text.
    
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
    
    # Since the API returns plain text, capture the text directly.
    result = response.text
    print(f"DEBUG: Received custom API response (first 100 chars): {result[:100]}...")
    return result

# Example usage:
if __name__ == "__main__":
    # Assume we have some sample email body text.
    sample_email_body = (
        "Dear Customer,\n\n"
        "We would like to inform you that your account has been flagged for suspicious activity.\n"
        "Please contact our compliance department immediately.\n\n"
        "Best regards,\n"
        "Your Bank"
    )
    instructions = get_instructions()
    analysis = invoke_custom_api(instructions, sample_email_body)
    print("Final Analysis:\n", analysis)
