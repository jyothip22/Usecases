import re

def format_email_body(body: str) -> str:
    """
    Formats an email body by normalizing newline characters,
    collapsing extra spaces and newlines, and ensuring clean, human-readable text.
    
    Steps:
    1. Convert Windows-style newlines (\r\n) and stray carriage returns (\r) into Unix-style newlines (\n).
    2. Collapse multiple spaces or tab characters into a single space.
    3. Collapse multiple consecutive newline sequences into a single blank line.
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
    # Collapse multiple newlines into a single blank line.
    body = re.sub(r'\n\s*\n', '\n\n', body)
    return body.strip()

def parse_msg(file_path: str) -> dict:
    """
    Parses an Outlook .msg file using the extract_msg package and returns a dictionary
    with the extracted metadata and the formatted email body.
    
    Debug statements trace key steps of the process.
    
    Args:
        file_path (str): The path to the .msg file.
    
    Returns:
        dict: A dictionary with keys "metadata" and "body".
    """
    print(f"Debug: Starting parse_msg for file: {file_path}")
    
    try:
        import extract_msg
    except ImportError as e:
        error_msg = "The extract_msg package is required for parsing .msg files. Install it via 'pip install extract_msg'."
        print(f"Error in parse_msg: {error_msg}")
        raise ImportError(error_msg) from e

    try:
        msg = extract_msg.Message(file_path)
    except Exception as e:
        print(f"Error reading .msg file: {e}")
        raise e

    metadata = {
        "From": msg.sender,
        "To": msg.to,
        "Cc": msg.cc,
        "Bcc": "",  # .msg files typically lack Bcc information.
        "Date": msg.date
    }
    print(f"Debug: Extracted metadata: {metadata}")

    body = msg.body
    if not body and hasattr(msg, "htmlBody"):
        body = msg.htmlBody
        print("Debug: Using HTML body fallback for .msg file.")
    else:
        print(f"Debug: Raw MSG body length: {len(body) if body else 0}")

    formatted_body = format_email_body(body) if body else ""
    print(f"Debug: Formatted MSG body length: {len(formatted_body)}")
    print(f"Debug: Completed parse_msg for file: {file_path}")
    return {"metadata": metadata, "body": formatted_body}

def parse_email(file_path: str) -> dict:
    """
    Dispatch function for parsing a file.
    Since this project now handles only .msg files, it calls parse_msg.
    
    Args:
        file_path (str): The path to the file.
    
    Returns:
        dict: Result from parse_msg.
    
    Raises:
        ValueError: If the file is not a .msg file.
    """
    print(f"Debug: In parse_email with file: {file_path}")
    if file_path.lower().endswith(".msg"):
        return parse_msg(file_path)
    else:
        error_msg = "Unsupported file format. Only .msg files are supported."
        print(f"Error: {error_msg}")
        raise ValueError(error_msg)
