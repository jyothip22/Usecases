import requests
import os

# Replace this with your actual FastAPI backend URL
API_URL = "http://localhost:8000/analyze-file"

# Path to a valid .msg file on your local system
FILE_PATH = "test_emails/sample_email.msg"

def test_upload_msg_file():
    if not os.path.exists(FILE_PATH):
        print(f"❌ File not found: {FILE_PATH}")
        return

    with open(FILE_PATH, "rb") as f:
        files = {"file": (os.path.basename(FILE_PATH), f, "application/vnd.ms-outlook")}

        print("📤 Uploading file to API...")
        response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return

        print("✅ File analyzed successfully.\n")

        data = response.json()

        print("📋 Metadata:")
        for key, value in data["metadata"].items():
            print(f"  {key}: {value}")

        print("\n🔍 Analysis:")
        for key, value in data["analysis"].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    test_upload_msg_file()
