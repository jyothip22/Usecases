import os
import uvicorn
import shutil
import tempfile

from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import custom modules.
# parser.py should define parse_email(file_path: str) -> dict.
# analyzer.py defines get_system_prompt() -> str and invoke_custom_api(tkd_name: str, input_text: str, system_prompt: str) -> str.
from parser import parse_email
from analyzer import get_system_prompt, invoke_custom_api

# Determine the absolute base directory (project folder) and set the archive folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_FOLDER = os.path.join(BASE_DIR, "emails_archive")

if not os.path.isdir(ARCHIVE_FOLDER):
    raise FileNotFoundError(f"Archive folder not found: {ARCHIVE_FOLDER}")

# Define a toolkit/model name (optionally set via environment variable)
TKD_NAME = os.getenv("TKD_NAME", "EmailMonitor1")

app = FastAPI(
    title="Email Compliance Analyzer API",
    description=(
        "Analyzes Outlook .msg email content for compliance and fraud detection "
        "by invoking a custom API with separate instructions and input text. "
        "Input can be provided via a file upload, a filename referencing an email stored locally, or plain text."
    ),
    version="1.0"
)

# ---------------------------
# Endpoint 1: Analyze via Filename (GET)
# ---------------------------
@app.get("/analyze-email")
async def analyze_email_endpoint(
    filename: str = Query(..., description="Filename of the .msg email to analyze")
):
    # Build the full file path.
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    print(f"DEBUG: Full file path: {file_path}")
    
    # Validate file existence and extension.
    if not os.path.exists(file_path):
        print("DEBUG: File not found, raising 404.")
        raise HTTPException(status_code=404, detail="File not found")
    if not filename.lower().endswith(".msg"):
        print("DEBUG: File is not a .msg file, raising 400.")
        raise HTTPException(status_code=400, detail="Only .msg files are supported")
    
    try:
        # Parse the email file.
        email_data = parse_email(file_path)
        print("DEBUG: Parsed email data:", email_data)
        email_body = email_data.get("body", "")
        print(f"DEBUG: Extracted email body (first 100 chars): {email_body[:100]}...")
        
        # Get the system prompt (instructions) from the analyzer.
        system_prompt = get_system_prompt()
        
        # Invoke the custom API.
        analysis = invoke_custom_api(TKD_NAME, email_body, system_prompt)
        print(f"DEBUG: Custom API analysis received (first 100 chars): {analysis[:100]}...")
        
        result = {
            "metadata": email_data.get("metadata", {}),
            "analysis": analysis
        }
        print("DEBUG: Assembled result:", result)
    except Exception as e:
        print("DEBUG: Exception in /analyze-email endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=result)

# ---------------------------
# Endpoint 2: Analyze via Text Input (POST)
# ---------------------------
class TextAnalysisRequest(BaseModel):
    text_input: str

@app.post("/analyze-text")
async def analyze_text_endpoint(request: TextAnalysisRequest):
    text_input = request.text_input
    print(f"DEBUG: Received text input (first 100 chars): {text_input[:100]}...")
    
    if not text_input or text_input.strip() == "":
        raise HTTPException(status_code=400, detail="Text input is empty.")
    
    try:
        system_prompt = get_system_prompt()
        analysis = invoke_custom_api(TKD_NAME, text_input, system_prompt)
        print(f"DEBUG: Custom API analysis (first 100 chars): {analysis[:100]}...")
        result = {"analysis": analysis}
        print("DEBUG: Assembled result for text analysis:", result)
    except Exception as e:
        print("DEBUG: Exception in /analyze-text endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=result)

# ---------------------------
# Endpoint 3: Analyze via File Upload (POST)
# ---------------------------
@app.post("/analyze-file")
async def analyze_file_endpoint(file: UploadFile = File(..., description="Upload a .msg file for analysis")):
    # Validate the file extension.
    if not file.filename.lower().endswith(".msg"):
        raise HTTPException(status_code=400, detail="Only .msg files are supported")
    
    try:
        # Save the uploaded file to a temporary file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".msg") as tmp:
            temp_file_path = tmp.name
            content = await file.read()  # Read the file as bytes.
            tmp.write(content)
        print(f"DEBUG: Saved uploaded file to temporary path: {temp_file_path}")
        
        # Parse the temporary file.
        email_data = parse_email(temp_file_path)
        print("DEBUG: Parsed email data:", email_data)
        email_body = email_data.get("body", "")
        print(f"DEBUG: Extracted email body (first 100 chars): {email_body[:100]}...")
        
        # Get the system prompt.
        system_prompt = get_system_prompt()
        
        # Invoke the custom API.
        analysis = invoke_custom_api(TKD_NAME, email_body, system_prompt)
        print(f"DEBUG: Custom API analysis received (first 100 chars): {analysis[:100]}...")
        
        # Assemble the result.
        result = {
            "metadata": email_data.get("metadata", {}),
            "analysis": analysis
        }
        print("DEBUG: Assembled result for file upload:", result)
    except Exception as e:
        print("DEBUG: Exception in /analyze-file endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up: remove the temporary file.
        try:
            os.remove(temp_file_path)
            print(f"DEBUG: Removed temporary file: {temp_file_path}")
        except Exception as e:
            print("DEBUG: Error removing temporary file:", str(e))
    
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
