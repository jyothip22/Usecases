import os
import openai
from dotenv import load_dotenv, find_dotenv

# Load environment variables if available.
_ = load_dotenv(find_dotenv())

# Configure Azure OpenAI connection details.
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE", "https://your-resource-name.openai.azure.com")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY", "your-azure-api-key")

def build_prompt(text: str) -> str:
    """
    Constructs a prompt for the language model, embedding the email content.
    
    Debug:
      Logs the first 100 characters of the constructed prompt.
    
    Args:
        text (str): The formatted email body.
    
    Returns:
        str: The prompt to be sent to the LLM.
    """
    prompt = f"""
You are a banking compliance and fraud detection expert. You are trained to detect and categorize potential fraudulent or non-compliant communications.
Analyze the following email content:
\"\"\"{text}\"\"\"
Provide:
- A summary of the email content.
- A list of red flags.
- Whether there is evidence of fraud or compliance issues.
- Suggested next action.
    """
    print(f"Debug: Built prompt (first 100 chars): {prompt[:100]}...")
    return prompt

def get_completion(prompt: str, engine: str = "gpt-35-turbo") -> str:
    """
    Sends the prompt to Azure OpenAI's ChatCompletion endpoint and returns the response.
    
    Debug:
      Prints the first 100 characters of the prompt and response.
    
    Args:
        prompt (str): The prompt text.
        engine (str, optional): The deployment name; defaults to "gpt-35-turbo".
    
    Returns:
        str: The response content from the LLM.
    """
    print("Debug: Calling Azure OpenAI with prompt:")
    print(f"Debug: {prompt[:100]}...")  # Print only the first 100 characters for brevity.
    
    messages = [{"role": "user", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            engine=engine,  # For Azure, this is your deployment name.
            messages=messages,
            temperature=0
        )
        content = response.choices[0].message.content
        print(f"Debug: Received response (first 100 chars): {content[:100]}...")
        return content
    except Exception as e:
        print(f"Error in get_completion: {e}")
        raise e
