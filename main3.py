import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
import uvicorn

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

# Set the path for the email archive folder (default is "./emails")
ARCHIVE_FOLDER = os.getenv("ARCHIVE_FOLDER", "./emails")

# Import custom modules.
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
    Analyze a single email file (.eml or .pst) from the archive folder.
    
    - For .eml files: Extract metadata and body, then perform analysis.
    - For .pst files: Extract all contained emails and analyze each one.
    """
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        email_data = parse_email(file_path)
        if "emails" in email_data:  # PST file returns a list of emails.
            analysis_results = []
            for email_item in email_data["emails"]:
                email_body = email_item.get("body", "")
                prompt = build_prompt(email_body)
                analysis = get_completion(prompt)
                analysis_results.append({
                    "metadata": email_item.get("metadata", {}),
                    "analysis": analysis
                })
            result = {"file_type": "pst", "emails": analysis_results}
        else:  # .eml file.
            email_body = email_data.get("body", "")
            prompt = build_prompt(email_body)
            analysis = get_completion(prompt)
            result = {
                "file_type": "eml",
                "metadata": email_data.get("metadata", {}),
                "analysis": analysis
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=result)

@app.get("/analyze-all-emails")
async def analyze_all_emails():
    """
    Analyze all email files (.eml and .pst) in the archive folder and return a list of analysis results.
    For PST files, each contained email is analyzed and its result returned.
    """
    results = []
    try:
        for filename in os.listdir(ARCHIVE_FOLDER):
            if filename.lower().endswith((".eml", ".pst")):
                file_path = os.path.join(ARCHIVE_FOLDER, filename)
                email_data = parse_email(file_path)
                if "emails" in email_data:
                    # PST file: process each email.
                    pst_results = []
                    for email_item in email_data["emails"]:
                        email_body = email_item.get("body", "")
                        prompt = build_prompt(email_body)
                        try:
                            analysis = get_completion(prompt)
                        except Exception as e:
                            analysis = f"Error during analysis: {str(e)}"
                        pst_results.append({
                            "metadata": email_item.get("metadata", {}),
                            "analysis": analysis
                        })
                    results.append({
                        "filename": filename,
                        "file_type": "pst",
                        "emails": pst_results
                    })
                else:
                    # .eml file.
                    email_body = email_data.get("body", "")
                    prompt = build_prompt(email_body)
                    try:
                        analysis = get_completion(prompt)
                    except Exception as e:
                        analysis = f"Error during analysis: {str(e)}"
                    results.append({
                        "filename": filename,
                        "file_type": "eml",
                        "metadata": email_data.get("metadata", {}),
                        "analysis": analysis
                    })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=results)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
