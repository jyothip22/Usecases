import re
import datetime

def format_email_body(body: str) -> str:
    """
    Formats an email body by normalizing newline characters,
    collapsing extra spaces and newlines, and ensuring clean, human-readable text.
    """
    # Normalize newlines to Unix-style.
    body = body.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple spaces or tabs into a single space.
    body = re.sub(r'[ \t]+', ' ', body)
    # Collapse multiple newlines into a single blank line.
    body = re.sub(r'\n\s*\n', '\n\n', body)
    return body.strip()

def parse_msg(file_path: str) -> dict:
    """
    Parses an Outlook .msg file using the extract_msg package and returns a dictionary
    with the extracted metadata and the formatted email body.
    """
    print(f"DEBUG: Starting parse_msg for file: {file_path}")
    
    try:
        import extract_msg
    except ImportError as e:
        error_msg = "The extract_msg package is required for parsing .msg files. Install it via 'pip install extract_msg'."
        print(f"ERROR in parse_msg: {error_msg}")
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
        "Bcc": "",  # .msg files typically lack Bcc information.
        "Date": msg.date
    }
    print(f"DEBUG: Extracted metadata before conversion: {metadata}")

    # Convert datetime objects to strings (if necessary).
    if isinstance(metadata.get("Date"), datetime.datetime):
        print(f"DEBUG: Converting datetime object {metadata['Date']} to string.")
        metadata["Date"] = metadata["Date"].isoformat()
    else:
        # In some cases, msg.date may already be a string.
        metadata["Date"] = str(metadata["Date"])
    print(f"DEBUG: Final metadata: {metadata}")

    body = msg.body
    if not body and hasattr(msg, "htmlBody"):
        body = msg.htmlBody
        print("DEBUG: Using HTML body as fallback for .msg file.")
    else:
        print(f"DEBUG: Raw MSG body length: {len(body) if body else 0}")

    formatted_body = format_email_body(body) if body else ""
    print(f"DEBUG: Formatted MSG body length: {len(formatted_body)}")
    print(f"DEBUG: Completed parse_msg for file: {file_path}")
    return {"metadata": metadata, "body": formatted_body}

def parse_email(file_path: str) -> dict:
    """
    Dispatch function for parsing a file.
    Since we now handle only .msg files, this calls parse_msg.
    """
    print(f"DEBUG: In parse_email with file: {file_path}")
    if file_path.lower().endswith(".msg"):
        return parse_msg(file_path)
    else:
        error_msg = "Unsupported file format. Only .msg files are supported."
        print(f"ERROR: {error_msg}")
        raise ValueError(error_msg)
