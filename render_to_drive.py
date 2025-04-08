import os
import re
import shutil
from datetime import datetime

# Configuration: Set the path to your Google Drive "Current Drafts" folder
google_drive_folder = "C:/path/to/Google Drive/Current Drafts"

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
def delete_existing_files(title):
    for file in os.listdir(google_drive_folder):
        if re.match(rf"^{re.escape(title)}-\d{{4}}-\d{{2}}-\d{{2}}\.wav$", file):
            os.remove(os.path.join(google_drive_folder, file))

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

    # Delete existing files with the same title
    delete_existing_files(title)

    # Move the most recent render to the Google Drive folder
    target_path = os.path.join(google_drive_folder, filename)
    try:
        shutil.move(recent_render, target_path)
        print("File moved to Google Drive folder successfully.")
    except Exception as e:
        print(f"Failed to move file to Google Drive folder: {e}")

# Run the script
if __name__ == "__main__":
    main()