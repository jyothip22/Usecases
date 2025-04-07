import os
import glob
from email import policy
from email.parser import BytesParser

def parse_email(file_path):
    """
    Parses an individual .eml file and extracts metadata and plain text content.
    """
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    metadata = {
        "From": msg.get('from'),
        "To": msg.get('to'),
        "BCC": msg.get('bcc'),
        "Subject": msg.get('subject'),
        "Date": msg.get('date')
    }

    # Try to get the plain text part first; fallback to HTML if needed
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain' and part.get_content() is not None:
                body = part.get_content()
                break
    else:
        body = msg.get_content()

    return metadata, body.strip()


def get_all_email_files(folder_path):
    """
    Lists all .eml files in the specified folder.
    """
    return glob.glob(os.path.join(folder_path, "*.eml"))
