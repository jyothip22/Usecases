import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

# Determine the absolute base directory (EmailMonitor1 folder) and set the archive folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_FOLDER = os.path.join(BASE_DIR, "emails_archive")

# Make sure the archive folder exists (it must already exist with your uploaded files)
if not os.path.isdir(ARCHIVE_FOLDER):
    raise FileNotFoundError(f"Archive folder not found: {ARCHIVE_FOLDER}")

# Import custom modules.
from parser import parse_email  # Now exclusively for .msg files
from analyzer import build_prompt, get_completion

app = FastAPI(
    title="Msg Email Compliance Analyzer API",
    description="Analyzes .msg email content for compliance and fraud detection in the banking sector.",
    version="1.0"
)

@app.get("/analyze-email")
async def analyze_email_endpoint(
    filename: str = Query(..., description="Filename of the .msg email to analyze")
):
    # Build full path for the requested file.
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    if not filename.lower().endswith(".msg"):
        raise HTTPException(status_code=400, detail="Only .msg files are supported")
    
    try:
        # Parse the email (.msg) file.
        email_data = parse_email(file_path)
        # email_data is a dict with keys "metadata" and "body"
        body = email_data.get("body", "")
        # Build the prompt to send to the LLM.
        prompt = build_prompt(body)
        # Get the analysis from the LLM.
        analysis = get_completion(prompt)
        result = {
            "metadata": email_data.get("metadata", {}),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=result)

@app.get("/analyze-all-emails")
async def analyze_all_emails():
    results = []
    try:
        files = os.listdir(ARCHIVE_FOLDER)
        print(f"Debug: Files in archive folder: {files}")
        for filename in files:
            if filename.lower().endswith(".msg"):
                file_path = os.path.join(ARCHIVE_FOLDER, filename)
                print(f"Debug: Processing file: {filename}")
                email_data = parse_email(file_path)
                body = email_data.get("body", "")
                prompt = build_prompt(body)
                try:
                    analysis = get_completion(prompt)
                except Exception as e:
                    analysis = f"Error during analysis: {str(e)}"
                results.append({
                    "filename": filename,
                    "metadata": email_data.get("metadata", {}),
                    "analysis": analysis
                })
            else:
                print(f"Debug: Skipping non-.msg file: {filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(content=results)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
