import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
import uvicorn

# Load environment variables from the .env file
_ = load_dotenv(find_dotenv())

# Set the path for the email archive folder (default is "./emails")
ARCHIVE_FOLDER = os.getenv("ARCHIVE_FOLDER", "./emails")

# Import our custom modules
from email_parser import parse_email
from analyzer import build_prompt, get_completion

app = FastAPI(
    title="Email Compliance Analyzer API",
    description="Analyzes email content for compliance and fraud detection in the banking sector.",
    version="1.0"
)

@app.get("/analyze-email")
async def analyze_email(filename: str = Query(..., description="Filename of the email to analyze")):
    """
    Analyzes a single email from the archive folder. The email is parsed to extract metadata
    and body content, which is then sent to the OpenAI API for compliance analysis.
    """
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        email_data = parse_email(file_path)
        email_body = email_data.get("body", "")
        prompt = build_prompt(email_body)
        analysis = get_completion(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content={
        "metadata": email_data.get("metadata", {}),
        "analysis": analysis
    })

@app.get("/analyze-all-emails")
async def analyze_all_emails():
    """
    Iterates over all .eml files in the archive folder, analyzes each email, and returns a list
    of analysis results along with the email metadata.
    """
    results = []
    try:
        for filename in os.listdir(ARCHIVE_FOLDER):
            if filename.lower().endswith(".eml"):
                file_path = os.path.join(ARCHIVE_FOLDER, filename)
                email_data = parse_email(file_path)
                email_body = email_data.get("body", "")
                prompt = build_prompt(email_body)
                try:
                    analysis = get_completion(prompt)
                except Exception as e:
                    analysis = f"Error during analysis: {str(e)}"
                results.append({
                    "filename": filename,
                    "metadata": email_data.get("metadata", {}),
                    "analysis": analysis
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=results)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
