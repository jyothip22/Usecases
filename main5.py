import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
import uvicorn

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

# Set the path for the email archive folder (default is "./emails")
ARCHIVE_FOLDER = os.getenv("ARCHIVE_FOLDER", "./emails")

# Import custom modules
from email_parser import parse_email
from analyzer import build_prompt, get_completion

app = FastAPI(
    title="Email Compliance Analyzer API",
    description="Analyzes email content for compliance and fraud detection in the banking sector.",
    version="1.0"
)

@app.get("/analyze-email")
async def analyze_email_endpoint(filename: str = Query(..., description="Filename of the email to analyze")):
    """
    Analyze a single email file (.eml, .msg, or .pst) from the archive folder.
    For PST files, each contained email is analyzed.
    """
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        email_data = parse_email(file_path)
        # Check if the result is a PST file that contains multiple emails.
        if "emails" in email_data:
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
        else:
            # For .eml or .msg files
            email_body = email_data.get("body", "")
            prompt = build_prompt(email_body)
            analysis = get_completion(prompt)
            result = {
                "file_type": "eml/msg",
                "metadata": email_data.get("metadata", {}),
                "analysis": analysis
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=result)

@app.get("/analyze-all-emails")
async def analyze_all_emails():
    """
    Analyze all email files (.eml, .msg, and .pst) in the archive folder.
    For PST files, each contained email is processed.
    """
    results = []
    try:
        for filename in os.listdir(ARCHIVE_FOLDER):
            # Process files with supported extensions.
            if filename.lower().endswith((".eml", ".msg", ".pst")):
                file_path = os.path.join(ARCHIVE_FOLDER, filename)
                email_data = parse_email(file_path)
                if "emails" in email_data:
                    # PST file: process each email message.
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
                    # .eml or .msg file.
                    email_body = email_data.get("body", "")
                    prompt = build_prompt(email_body)
                    try:
                        analysis = get_completion(prompt)
                    except Exception as e:
                        analysis = f"Error during analysis: {str(e)}"
                    results.append({
                        "filename": filename,
                        "file_type": "eml/msg",
                        "metadata": email_data.get("metadata", {}),
                        "analysis": analysis
                    })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return JSONResponse(content=results)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
