import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

CUSTOM_API_URL = os.getenv("CUSTOM_API_URL", "http://10.39.16.10:8000/query")

def get_system_prompt() -> str:
    return """
You are a compliance analyst trained to detect and categorize potential fraudulent or non-compliant communication within a regulated banking environment.

Given an email text, analyze and return your response strictly in JSON with the following fields:

{
  "summary": "<Brief summary of the email>",
  "red_flags": ["<list any suspicious phrases or behaviors>"],
  "violation_detected": true | false,
  "violation_type": "<One of: Guarantees & Assurances, Gifts & Entertainment, Front Running, or None>",
  "explanation": "<Explain why this is a violation or not>",
  "recommended_action": "<e.g., Escalate to compliance team, Request more info, No action needed>"
}

If no red flags are found, set violation_type to "None", violation_detected to false, and recommended_action to "No action needed".
""".strip()

def invoke_custom_api(tkd_name: str, input_text: str, system_prompt: str) -> dict:
    if not input_text or input_text.strip() == "":
        raise ValueError("Input text is empty. Cannot invoke custom API without email content.")

    payload = {
        "tkd_name": tkd_name,
        "input": input_text,
        "system_prompt": system_prompt
    }
    print("DEBUG: Invoking custom API with payload:", payload)

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(CUSTOM_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        # Try to parse the response as JSON
        try:
            parsed_response = json.loads(response.text)
            print("DEBUG: Parsed JSON response from LLM.")
            return parsed_response
        except json.JSONDecodeError as e:
            print("ERROR: Invalid JSON response from LLM:", response.text)
            raise ValueError("Custom API returned invalid JSON") from e

    except requests.exceptions.HTTPError as he:
        print("ERROR: HTTP error when invoking custom API:", he)
        print("ERROR: Response Content:", response.text)
        raise he
    except Exception as e:
        print("ERROR invoking custom API:", e)
        raise e
