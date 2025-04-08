import email
from email import policy
from email.parser import BytesParser

def parse_eml(file_path: str) -> dict:
    """
    Parses a MIME formatted email (.eml) and returns a dict with metadata and body.
    """
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    metadata = {
        "From": msg.get("From", ""),
        "To": msg.get("To", ""),
        "Cc": msg.get("Cc", ""),
        "Bcc": msg.get("Bcc", ""),
        "Date": msg.get("Date", "")
    }

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = part.get("Content-Disposition", "")
            if part.get_content_type() == "text/plain" and "attachment" not in content_disposition:
                body += part.get_content()
    else:
        body = msg.get_content()

    return {"metadata": metadata, "body": body}

def parse_msg(file_path: str) -> dict:
    """
    Parses an Outlook email (.msg) and returns a dict with metadata and body.
    Requires the extract_msg package.
    """
    try:
        import extract_msg
    except ImportError:
        raise ImportError("The extract_msg package is required to parse .msg files. Install it via 'pip install extract_msg'.")

    msg = extract_msg.Message(file_path)
    msg.extract()  # Optional: extracts attachments if needed.
    metadata = {
        "From": msg.sender,
        "To": msg.to,
        "Cc": msg.cc,
        "Bcc": "",  # .msg files typically do not include Bcc information.
        "Date": msg.date
    }
    body = msg.body
    # If plain text body is empty, fallback to the HTML body.
    if not body and msg.htmlBody:
        body = msg.htmlBody
    return {"metadata": metadata, "body": body}

def parse_pst(file_path: str) -> list:
    """
    Parses a PST file and returns a list of email dictionaries (each with metadata and body).
    Requires the pypff module.
    """
    try:
        import pypff
    except ImportError:
        raise ImportError("The pypff module is required to parse PST files. Please install it.")

    pst_file = pypff.file()
    pst_file.open(file_path)
    emails = []

    def recursive_folder(folder):
        # Process sub-folders recursively.
        for i in range(folder.number_of_sub_folders):
            sub_folder = folder.get_sub_folder(i)
            recursive_folder(sub_folder)
        # Process messages in the current folder.
        for j in range(folder.number_of_sub_messages):
            message = folder.get_sub_message(j)
            metadata = {
                "From": getattr(message, "sender_name", ""),
                "To": getattr(message, "display_to", ""),
                "Cc": getattr(message, "display_cc", ""),
                "Bcc": "",  # Bcc is generally not available.
                "Date": str(message.client_submit_time) if hasattr(message, "client_submit_time") and message.client_submit_time else ""
            }
            body = ""
            if hasattr(message, "plain_text_body") and message.plain_text_body:
                body = message.plain_text_body
            elif hasattr(message, "html_body") and message.html_body:
                body = message.html_body
            emails.append({"metadata": metadata, "body": body})

    root_folder = pst_file.get_root_folder()
    recursive_folder(root_folder)
    pst_file.close()
    return emails

def parse_email(file_path: str) -> dict:
    """
    Dispatch function that inspects the file extension and calls the appropriate parsing function:
      - For .eml, returns a dict with metadata and body.
      - For .msg, returns a dict with metadata and body.
      - For .pst, returns a dict with key "emails" containing a list of email dicts.
    """
    lower_path = file_path.lower()
    if lower_path.endswith(".pst"):
        return {"emails": parse_pst(file_path)}
    elif lower_path.endswith(".eml"):
        return parse_eml(file_path)
    elif lower_path.endswith(".msg"):
        return parse_msg(file_path)
    else:
        raise ValueError("Unsupported file format. Only .eml, .msg, and .pst files are supported.")
