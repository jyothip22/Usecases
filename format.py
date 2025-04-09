import re

def format_email_body(body: str) -> str:
    """
    Formats an Outlook email body by normalizing newline characters,
    collapsing extra spaces, and ensuring clean, human-readable text.
    
    Steps:
    1. Convert Windows-style newlines (\r\n) and any stray \r to Unix newlines (\n).
    2. Collapse multiple spaces and tabs into a single space.
    3. Collapse multiple consecutive newline sequences into a single blank line.
    4. Strip leading and trailing whitespace.
    
    Args:
        body (str): The raw email body text.
    
    Returns:
        str: The formatted email body.
    """
    # Normalize newlines to Unix style
    body = body.replace('\r\n', '\n').replace('\r', '\n')
    
    # Collapse multiple spaces (or tab characters) into a single space
    body = re.sub(r'[ \t]+', ' ', body)
    
    # Collapse multiple newlines into at most a double newline (one blank line)
    body = re.sub(r'\n\s*\n', '\n\n', body)
    
    # Remove extra newlines at the beginning and end
    body = body.strip()
    
    return body

# Example usage:
if __name__ == "__main__":
    raw_body = "Hello,\r\n\r\nThis is a test email body.\r\n\r\nRegards,\r\nSender"
    formatted_body = format_email_body(raw_body)
    print("Formatted Email Body:")
    print(formatted_body)
