import os
import json
import uuid
import datetime
import boto3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

# Determine the absolute base directory (EmailMonitor1 folder) and set the archive folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_FOLDER = os.path.join(BASE_DIR, "emails_archive")

# Ensure the archive folder exists.
if not os.path.isdir(ARCHIVE_FOLDER):
    raise FileNotFoundError(f"Archive folder not found: {ARCHIVE_FOLDER}")

# Import custom modules.
from parser import parse_email  # This now handles only .msg files.
from analyzer import build_prompt, get_completion

# Setup DynamoDB connection.
# If running locally or in an environment with proper IAM roles, boto3 will load your credentials.
# Adjust region and table name as needed.
DDB_TABLE_NAME = os.getenv("DYNAMODB_TABLE", "EmailAnalysis")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")  # Modify region if required
ddb_table = dynamodb.Table(DDB_TABLE_NAME)

def persist_result_to_dynamodb(filename: str, email_data: dict, analysis: str):
    """
    Persists the email analysis result to DynamoDB.
    
    Args:
        filename (str): The name of the analyzed email file.
        email_data (dict): The parsed email data, including "metadata" and "body".
        analysis (str): The response from the LLM.
    """
    record = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "metadata": email_data.get("metadata", {}),
        "body": email_data.get("body", ""),
        "analysis": analysis,
        "timestamp": datetime.datetime.utcnow().isoformat()  # ISO formatted timestamp.
    }
    print("DEBUG: Persisting record to DynamoDB:", record)
    ddb_table.put_item(Item=record)

app = FastAPI(
    title="Msg Email Compliance Analyzer API",
    description="Analyzes .msg email content for compliance and fraud detection in the banking sector.",
    version="1.0"
)

@app.get("/analyze-email")
async def analyze_email_endpoint(
    filename: str = Query(..., description="Filename of the .msg email to analyze")
):
    # Build the full file path.
    file_path = os.path.join(ARCHIVE_FOLDER, filename)
    print(f"DEBUG: Full file path: {file_path}")

    if not os.path.exists(file_path):
        print("DEBUG: File not found, raising 404.")
        raise HTTPException(status_code=404, detail="File not found")
    if not filename.lower().endswith(".msg"):
        print("DEBUG: File is not a .msg file, raising 400.")
        raise HTTPException(status_code=400, detail="Only .msg files are supported")
    
    try:
        # Parse the .msg file.
        email_data = parse_email(file_path)
        print("DEBUG: Parsed email data:", email_data)
        
        # Extract the formatted email body.
        body = email_data.get("body", "")
        print(f"DEBUG: Extracted email body (first 100 chars): {body[:100]}...")
        
        # Build the prompt for LLM analysis.
        prompt = build_prompt(body)
        print(f"DEBUG: Built prompt (first 100 chars): {prompt[:100]}...")
        
        # Get the analysis from LLM.
        analysis = get_completion(prompt)
        print(f"DEBUG: LLM analysis received (first 100 chars): {analysis[:100]}...")
        
        # Assemble the result.
        result = {
            "metadata": email_data.get("metadata", {}),
            "analysis": analysis
        }
        print("DEBUG: Assembled result:", result)
        
        # Attempt to serialize result (for debugging purposes).
        try:
            serialized = json.dumps(result)
            print("DEBUG: Successfully serialized result (first 200 chars):", serialized[:200])
        except Exception as se:
            print("DEBUG: Error serializing result:", se)
            raise se

        # Persist the result to DynamoDB.
        persist_result_to_dynamodb(filename, email_data, analysis)
        
    except Exception as e:
        print("DEBUG: Exception in /analyze-email endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    print("DEBUG: Returning JSONResponse for /analyze-email endpoint.")
    return JSONResponse(content=result)

@app.get("/analyze-all-emails")
async def analyze_all_emails():
    results = []
    try:
        files = os.listdir(ARCHIVE_FOLDER)
        print(f"DEBUG: Files in archive folder: {files}")
        
        for filename in files:
            if filename.lower().endswith(".msg"):
                file_path = os.path.join(ARCHIVE_FOLDER, filename)
                print(f"DEBUG: Processing file: {filename} at path: {file_path}")
                try:
                    email_data = parse_email(file_path)
                    print(f"DEBUG: Parsed data for {filename}:", email_data)
                    
                    body = email_data.get("body", "")
                    print(f"DEBUG: Email body for {filename} (first 100 chars): {body[:100]}...")
                    
                    prompt = build_prompt(body)
                    print(f"DEBUG: Built prompt for {filename} (first 100 chars): {prompt[:100]}...")
                    
                    analysis = get_completion(prompt)
                    print(f"DEBUG: LLM analysis for {filename} (first 100 chars): {analysis[:100]}...")
                    
                    result = {
                        "filename": filename,
                        "metadata": email_data.get("metadata", {}),
                        "analysis": analysis
                    }
                    print(f"DEBUG: Assembled result for {filename}:", result)
                    results.append(result)
                    
                    # Persist each result to DynamoDB.
                    persist_result_to_dynamodb(filename, email_data, analysis)
                    
                except Exception as e:
                    error_message = f"Error processing {filename}: {str(e)}"
                    print("DEBUG:", error_message)
                    results.append({"filename": filename, "error": error_message})
            else:
                print(f"DEBUG: Skipping non-.msg file: {filename}")
    except Exception as e:
        print("DEBUG: Exception in /analyze-all-emails endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        serialized_results = json.dumps(results)
        print("DEBUG: Successfully serialized aggregated results (first 200 chars):", serialized_results[:200])
    except Exception as se:
        print("DEBUG: Error serializing aggregated results:", se)
        raise se

    print("DEBUG: Returning JSONResponse for /analyze-all-emails endpoint.")
    return JSONResponse(content=results)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
