import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables if available.
#_ = load_dotenv(find_dotenv())

# Set the custom API endpoint URL.
#CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "https://your-custom-api.example.com/analyze")

TKD_NAME = "EmailMonitor1"
sample_input = "Make this deal happen before the market hears the news"

def get_instructions() -> str:
    instructions = """
    You are a compliance analyst trained to detect and categorize potential fraudulent ot non compliant communication within a regualted banking environment.
Given a communication excerpt, identify whether it suggests suspicious or fraudulent activity.If yes, assign it to one of the following 
categories (based on the nature of the issue)
1.Gaurantees & ASsurances
2.Gifts & Entertainment
3.Front Running

Instructions:
1.Read the message carefully.
2.if it contains launguage suggesting fraud, ethical behavior, or regulatory risk, classify it into one of the most relevant category
and respond: "Suspicious Activity detected"
3.if no suspicious activity is detected, respond: "No suspicious activity detected"
4.Provide a breif explanation of the reasoning behind the classfication.

Use the below examples to assign a category to the communcation text provided
Example Input 1:
Deal is a slam dunk, should make killing
Category: Gaurantees & ASsurances
Explanation: This message implies certainity about the outcome of a financial deal, which may mislead clients or reflect inappropriate 
communication

Example Input 2:
The massage parlour expense was coded as consulting
Output: 
Category: Gifts & Entertainment
Explanation: Misclassification of personal or entertainment expenses as business consulting suggests a potential compliance violation

Example Input 3:
Our firm is advising on a confidential take over of JKL company. If you get in now, there's likely big upside.
Output:
Category: Front Running
Explanation:The message discloses confidential information about a takeover involving JKL company, and encourages someone to act on it before the information becomes public. This is a classic example of insider trading and front running behavior."
    """
    # .strip() removes any leading/trailing whitespace/newlines.
    result = instructions.strip()
    print(f"DEBUG: Instructions (first 100 chars): {result[:100]}...")
    return result

def invoke_custom_api(tkd_name: str, input: str, system_prompt: str) -> str
    payload = {
        "tkd_name": tkd_name,
        "input": input
        "system_prompt": system_prompt
    
    }
    print("DEBUG: Invoking custom API with payload:")
    print(f"DEBUG: {payload}")
    
    try:
        response = requests.post(CUSTOM_API_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error: HTTP error when invoking TKD API:", err)
        print("Error: Response Content", response.text)
        raise err
    except Exception as e:
        print("ERROR invoking custom API:", e)
        raise e
    
    # Since the API returns plain text, capture the text directly.
    result = response.text
    print(f"DEBUG: Received custom API response (first 100 chars): {result[:100]}...")
    return result

# Example usage:
if __name__ == "__main__":
    
    instructions = get_instructions()
    analysis = invoke_custom_api(TKD_NAME, sample_input, instructions)
    print("Final Analysis:\n", analysis)
