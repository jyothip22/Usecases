from email import policy
from email.parser import BytesParser
import os

def parse_email(file_path: str) -> dict:
    file_path = os.path.abspath(file_path)
    file_lower = file_path.lower()

    if file_lower.endswith(".msg"):
        import extract_msg
        msg = extract_msg.Message(file_path)
        msg.extract()

        metadata = {
            "From": msg.sender,
            "To": msg.to,
            "Cc": msg.cc,
            "Bcc": "",
            "Subject": msg.subject,
            "Date": msg.date
        }
        body = msg.body or msg.htmlBody or ""
        return {"metadata": metadata, "body": body.strip()}

    elif file_lower.endswith(".eml"):
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        metadata = {
            "From": msg.get("From", ""),
            "To": msg.get("To", ""),
            "Cc": msg.get("Cc", ""),
            "Bcc": msg.get("Bcc", ""),
            "Subject": msg.get("Subject", ""),
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

        return {"metadata": metadata, "body": body.strip()}

    else:
        raise ValueError("Unsupported file type. Supported: .eml, .msg")
