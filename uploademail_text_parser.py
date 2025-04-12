import re
import os

def format_email_body(body: str) -> str:
    """
    Formats an email body by normalizing newline characters,
    collapsing extra spaces and newlines, and ensuring clean, human-readable text.
    
    Steps:
      1. Convert Windows-style newlines (\r\n) and stray carriage returns (\r) into Unix-style newlines (\n).
      2. Collapse multiple spaces or tab characters into a single space.
      3. Collapse multiple consecutive newlines into a single blank line.
      4. Trim leading and trailing whitespace.
    
    Args:
        body (str): The raw email body text.
    
    Returns:
        str: The formatted email body.
    """
    # Normalize newlines to Unix-style.
    body = body.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple spaces or tabs into a single space.
    body = re.sub(r'[ \t]+', ' ', body)
    # Collapse multiple consecutive newlines into one blank line.
    body = re.sub(r'\n\s*\n', '\n\n', body)
    return body.strip()

def parse_msg(file_path: str) -> dict:
    """
    Parses an Outlook email (.msg) file using the extract_msg package and returns a dictionary
    with the extracted metadata and a formatted email body.
    
    The metadata includes keys such as "From", "To", "Cc", "Bcc", and "Date".
    
    Args:
        file_path (str): The path to the .msg file.
    
    Returns:
        dict: A dictionary with two keys:
                - "metadata": A dictionary with email header information.
                - "body": A string containing the formatted email content.
    """
    print(f"DEBUG: Starting parse_msg for file: {file_path}")
    try:
        import extract_msg
    except ImportError as e:
        error_msg = "The extract_msg package is required to parse .msg files. Please install it via 'pip install extract_msg'."
        print("ERROR in parse_msg:", error_msg)
        raise ImportError(error_msg) from e

    try:
        msg = extract_msg.Message(file_path)
    except Exception as e:
        print(f"ERROR reading .msg file: {e}")
        raise e

    metadata = {
        "From": msg.sender,
        "To": msg.to,
        "Cc": msg.cc,
        "Bcc": "",  # .msg files typically do not include Bcc information.
        "Date": msg.date
    }
    print(f"DEBUG: Extracted metadata: {metadata}")
    
    body = msg.body
    if not body or body.strip() == "":
        if hasattr(msg, "htmlBody"):
            body = msg.htmlBody
            print("DEBUG: Falling back to HTML body for .msg file.")
    print(f"DEBUG: Raw MSG body length: {len(body) if body else 0}")
    
    formatted_body = format_email_body(body) if body else ""
    print(f"DEBUG: Formatted MSG body length: {len(formatted_body)}")
    print(f"DEBUG: Completed parse_msg for file: {file_path}")
    
    return {"metadata": metadata, "body": formatted_body}

def parse_email(file_path: str) -> dict:
    """
    Dispatch function that determines the file type based on extension and invokes the appropriate parser.
    Currently supports only .msg files.
    
    Args:
        file_path (str): The path to the file.
    
    Returns:
        dict: The parsed email data.
    
    Raises:
        ValueError: If the file format is unsupported.
    """
    print(f"DEBUG: In parse_email with file: {file_path}")
    if file_path.lower().endswith(".msg"):
        return parse_msg(file_path)
    else:
        error_msg = "Unsupported file format. Only .msg files are supported."
        print("ERROR:", error_msg)
        raise ValueError(error_msg)
