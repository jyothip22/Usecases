import os
from email_parser import parse_email

def main():
    # Hard-code the archive folder name.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    archive_folder = os.path.join(base_dir, "emails")

    # Check if the archive folder exists.
    if not os.path.exists(archive_folder):
        print(f"Archive folder not found: {archive_folder}")
        return

    # Process all files with supported extensions (.eml or .pst) in the folder.
    for filename in os.listdir(archive_folder):
        # Optionally, filter by file extensions.
        if filename.lower().endswith((".eml", ".pst")):
            file_path = os.path.join(archive_folder, filename)
            print(f"\nProcessing file: {filename}")
            try:
                result = parse_email(file_path)
                print("Parsed Result:")
                print(result)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        else:
            print(f"Skipping unsupported file: {filename}")

if __name__ == "__main__":
    main()
