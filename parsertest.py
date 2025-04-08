import os
from email_parser import parse_email, get_all_email_files


print("hello from parser test")

folder = "EmailSurvelliance/email_archive"
print("Full path:", os.path.abspath(folder))

files = get_all_email_files(folder)
print("Looking for emails in:", folder)
print("Found files:", files)
for file in files:
    metadata, content = parse_email(file)
    print(f"--- {file} ---")
    print("Metadata:", metadata)
    print("Content:", content[:300], "...\n")  # Just print first 300 chars
