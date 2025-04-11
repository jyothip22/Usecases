import os
import uvicorn
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

# Import custom modules
from parser import parse_email
from analyzer import get_system_prompt, invoke_custom_api

# Toolkit/model identifier
TKD_NAME = os.getenv("TKD_NAME", "EmailMonitor1")

# FastAPI app definition
app = FastAPI(
    title="Msg Email Compliance Analyzer API",
    description=(
        "Analyzes uploaded .msg email content for compliance and fraud detection by invoking "
        "a custom API with separate instructions and input text."
    ),
    version="1.0"
)

@app.post("/upload-email")
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

        # Analyze email content
        email_body = email_data.get("body", "")
        system_prompt = get_system_prompt()
        analysis = invoke_custom_api(TKD_NAME, email_body, system_prompt)

        result = {
            "metadata": email_data.get("metadata", {}),
            "analysis": analysis
        }

        return JSONResponse(content=result)

    except Exception as e:
        print("ERROR processing uploaded email:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
