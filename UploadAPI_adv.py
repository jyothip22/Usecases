import os
import uvicorn
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
from analyzer import get_system_prompt, invoke_custom_api
from parser import parse_email

class AnalysisResult(BaseModel):
    summary: str
    red_flags: List[str]
    violation_detected: bool
    violation_type: str
    explanation: str
    recommended_action: str

class EmailAnalysisResponse(BaseModel):
    metadata: Dict[str, Any]
    analysis: AnalysisResult

TKD_NAME = os.getenv("TKD_NAME", "EmailMonitor1")

app = FastAPI(
    title="Msg Email Compliance Analyzer API",
    description=(
        "Analyzes uploaded .msg email content for compliance and fraud detection by invoking "
        "a custom API with separate instructions and input text."
    ),
    version="1.0"
)

@app.post("/upload-email", response_model=EmailAnalysisResponse)
async def upload_email(file: UploadFile = File(...)):
    print(f"DEBUG: Received uploaded file: {file.filename}")

    if not file.filename.lower().endswith(".msg"):
        raise HTTPException(status_code=400, detail="Only .msg files are supported")

    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".msg") as tmp_file:
            tmp_path = tmp_file.name
            content = await file.read()
            tmp_file.write(content)

        print(f"DEBUG: Saved uploaded file to temporary path: {tmp_path}")

        # Parse the saved file
        email_data = parse_email(tmp_path)
        print("DEBUG: Parsed email data")

        # Analyze content
        email_body = email_data.get("body", "")
        system_prompt = get_system_prompt()
        analysis_dict = invoke_custom_api(TKD_NAME, email_body, system_prompt)

        # Validate and return structured analysis
        analysis = AnalysisResult(**analysis_dict)

        return EmailAnalysisResponse(
            metadata=email_data.get("metadata", {}),
            analysis=analysis
        )

    except Exception as e:
        print("ERROR processing uploaded email:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
