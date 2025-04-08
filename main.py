# main.py
from fastapi import FastAPI, HTTPException
from email_parser import parse_email
from analyzer import analyze_email
import os

app = FastAPI()

@app.get("/analyze-email/")
def analyze_single_email(file_name: str):
    archive_folder = "email_archive"
    file_path = os.path.join(archive_folder, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Email file not found.")
    
    metadata, content = parse_email(file_path)
    try:
        analysis = analyze_email(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "metadata": metadata,
        "analysis": analysis
    }
