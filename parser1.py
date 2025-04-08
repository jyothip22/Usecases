import email
from email import policy
from email.parser import BytesParser

def parse_email(file_path: str) -> dict:
    """
    Parses an email file (either Outlook .msg or MIME .eml format) and extracts metadata and text content.
    """
    if file_path.lower().endswith(".msg"):
        try:
            import extract_msg
        except ImportError:
            raise ImportError("The extract_msg package is required to parse Outlook .msg files. Install it via 'pip install extract_msg'.")
        
        # Parse the Outlook .msg file
        msg = extract_msg.Message(file_path)
        msg.extract()  # Optionally extract attachments or additional content.
        metadata = {
            "From": msg.sender,
            "To": msg.to,
            "Cc": msg.cc,
            "Bcc": "",  # Bcc is generally not available in .msg files.
            "Date": msg.date
        }
        # Prefer the plain text body; fall back to HTML if necessary.
        body = msg.body
        if not body and msg.htmlBody:
            body = msg.htmlBody
        return {"metadata": metadata, "body": body}
    else:
        # Assume it's a MIME formatted (.eml) file.
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
                # Only extract text if it is not an attachment.
                if part.get_content_type() == "text/plain" and "attachment" not in content_disposition:
                    body += part.get_content()
        else:
            body = msg.get_content()
        
        return {"metadata": metadata, "body": body}
