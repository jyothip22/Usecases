import requests

BASE_URL = "http://localhost:8000"

def test_get_analyze_email(filename: str):
    """
    Tests the GET /analyze-email endpoint by sending a filename query parameter.
    The file should be in the server's emails_archive folder.
    """
    url = f"{BASE_URL}/analyze-email"
    params = {"filename": filename}
    print(f"Testing GET /analyze-email with filename: {filename}")
    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw Response Text:", response.text)

def test_post_analyze_text(text_input: str):
    """
    Tests the POST /analyze-text endpoint by sending a JSON payload with a key 'text_input'
    that contains the email content.
    """
    url = f"{BASE_URL}/analyze-text"
    json_payload = {"text_input": text_input}
    print("\nTesting POST /analyze-text with text input:")
    print(text_input[:100] + "...\n")
    response = requests.post(url, json=json_payload)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw Response Text:", response.text)

def test_post_analyze_file(filepath: str):
    """
    Tests the POST /analyze-file endpoint by uploading a file.
    The file should be an Outlook .msg file.
    """
    url = f"{BASE_URL}/analyze-file"
    print(f"\nTesting POST /analyze-file with file: {filepath}")
    try:
        with open(filepath, "rb") as f:
            files = {"file": (filepath, f, "application/octet-stream")}
            response = requests.post(url, files=files)
        print("Status Code:", response.status_code)
        try:
            print("Response JSON:", response.json())
        except Exception as e:
            print("Error parsing JSON:", e)
            print("Raw Response Text:", response.text)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print("Error during file upload test:", e)

if __name__ == "__main__":
    # Replace with the name of an existing .msg file in the server's emails_archive folder.
    test_filename = "test.msg"
    test_get_analyze_email(test_filename)
    
    # Test direct text analysis. Use a sample email text.
    sample_text = (
        "Dear Customer,\n\n"
        "Your account has been flagged for suspicious activity. "
        "Please contact our compliance department immediately.\n\n"
        "Best regards,\nYour Bank"
    )
    test_post_analyze_text(sample_text)
    
    # Test file upload. Ensure that a file named 'test.msg' exists in your project directory.
    test_post_analyze_file("test.msg")
