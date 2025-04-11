import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

# Import custom modules.
# parser.py should define parse_email(file_path: str) -> dict
# analyzer.py should define get_system_prompt() -> str and invoke_custom_api(tkd_name: str, input_text: str, system_prompt: str) -> str
from parser import parse_email
from analyzer import get_system_prompt, invoke_custom_api

# Determine the absolute base directory and set the archive folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_FOLDER = os.path.join(BASE_DIR, "emails_archive")

# Ensure the archive folder exists.
if not os.path.isdir(ARCHIVE_FOLDER):
    raise FileNotFoundError(f"Archive folder not found: {ARCHIVE_FOLDER}")

# Define a toolkit/model name (can also be set via environment variable).
TKD_NAME = os.getenv("TKD_NAME", "EmailMonitor1")

app = FastAPI(
    title="Msg Email Compliance Analyzer API",
    description=(
        "Analyzes .msg email content for compliance and fraud detection by invoking "
        "a custom API with separate instructions and input text."
    ),
    version="1.0"
)

@app.get("/analyze-email")
async def analyze_email_endpoint(
    filename: str = Query(..., description="Filename of the .msg email to analyze")
):
    # Build the full file path.
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    print(f"DEBUG: Full file path: {file_path}")

    # Validate file existence.
    if not os.path.exists(file_path):
        print("DEBUG: File not found, raising 404")
        raise HTTPException(status_code=404, detail="File not found")
    # Validate that the file extension is .msg.
    if not filename.lower().endswith(".msg"):
        print("DEBUG: File is not a .msg file, raising 400")
        raise HTTPException(status_code=400, detail="Only .msg files are supported")

    try:
        # Parse the .msg file to extract metadata and formatted email body.
        email_data = parse_email(file_path)
        print("DEBUG: Parsed email data:", email_data)

        # Extract the email body (formatted) from the parsed results.
        email_body = email_data.get("body", "")
        print(f"DEBUG: Extracted email body (first 100 chars): {email_body[:100]}...")

        # Retrieve the system prompt (instructions) using the analyzer function.
        system_prompt = get_system_prompt()

        # Invoke the custom API, sending the toolkit name, email body, and the system prompt.
        analysis = invoke_custom_api(TKD_NAME, email_body, system_prompt)
        print(f"DEBUG: Custom API analysis received (first 100 chars): {analysis[:100]}...")

        # Assemble the response result.
        result = {
            "metadata": email_data.get("metadata", {}),
            "analysis": analysis
        }
        print("DEBUG: Assembled result:", result)
    except Exception as e:
        print("DEBUG: Exception in /analyze-email endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    print("DEBUG: Returning JSONResponse for /analyze-email endpoint.")
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
