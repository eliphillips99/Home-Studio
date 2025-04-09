import os
import re
import shutil
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Function to read the Google Drive folder ID from a text file
def get_google_drive_folder_id():
    ref_file_path = os.path.join("ref", "google_drive_folder_id.txt")
    with open(ref_file_path, "r") as file:
        return file.read().strip()

# Authenticate with Google Drive API
def authenticate_google_drive():
    credentials = Credentials.from_service_account_file(
        "C:\\Users\\eligp\\AppData\\Roaming\\gspread\\credentials.json",
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    return build("drive", "v3", credentials=credentials)

# Function to upload a file to Google Drive
def upload_to_google_drive(service, file_path, folder_id):
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    return uploaded_file.get("id")

# Function to get the most recent render file
def get_most_recent_render(project_path):
    most_recent_file = None
    most_recent_time = 0

    # Iterate through files in the project directory
    for file in os.listdir(project_path):
        full_path = os.path.join(project_path, file)
        if os.path.isfile(full_path) and file.endswith(".wav"):
            file_time = os.path.getmtime(full_path)
            if file_time > most_recent_time:
                most_recent_file = full_path
                most_recent_time = file_time

    return most_recent_file

# Function to extract the title from the render filename
def extract_title(filename):
    match = re.match(r"^(.*?)-\d{4}-\d{2}-\d{2}\.wav$", filename)
    return match.group(1) if match else None

# Function to delete existing files with the same title in the Google Drive folder
def delete_existing_files(service, title, folder_id):
    query = f"'{folder_id}' in parents and name contains '{title}' and mimeType='audio/wav'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    for file in results.get("files", []):
        service.files().delete(fileId=file["id"]).execute()

# Main script logic
def main():
    project_path = os.getcwd()  # Get the current working directory
    recent_render = get_most_recent_render(project_path)
    if not recent_render:
        print("No recent render found.")
        return

    filename = os.path.basename(recent_render)  # Extract filename
    title = extract_title(filename)
    if not title:
        print("Could not extract title from render filename.")
        return

    # Authenticate with Google Drive
    service = authenticate_google_drive()

    # Get the Google Drive folder ID from the text file
    google_drive_folder_id = get_google_drive_folder_id()

    # Delete existing files with the same title in the Google Drive folder
    delete_existing_files(service, title, google_drive_folder_id)

    # Upload the most recent render to the Google Drive folder
    try:
        upload_to_google_drive(service, recent_render, google_drive_folder_id)
        print("File uploaded to Google Drive folder successfully.")
    except Exception as e:
        print(f"Failed to upload file to Google Drive folder: {e}")

# Run the script
if __name__ == "__main__":
    main()