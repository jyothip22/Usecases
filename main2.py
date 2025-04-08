from fastapi import FastAPI, HTTPException
from email_parser import parse_email
from analyzer import analyze_email_text
import os

app = FastAPI()

@app.get("/analyze-email/")
def analyze_email(file_name: str):
    folder = "email_archive"
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Email file not found.")

    try:
        parsed = parse_email(file_path)
        metadata = parsed["metadata"]
        body = parsed["body"]

        if not body:
            raise HTTPException(status_code=400, detail="Email body is empty.")

        analysis = analyze_email_text(body)
        return {
            "metadata": metadata,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
