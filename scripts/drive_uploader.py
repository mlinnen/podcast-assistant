import os
import pickle
import mimetypes
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes required for Drive Integration
# Note: Adding Drive scope to existing YouTube scope to have a single auth flow if wanted, 
# or strictly Drive scope here. 
# Best practice: use a superset of scopes if sharing token.pickle, or different tokens.
# Main.py currently doesn't manage token sharing well if we change scopes, so we assume
# token.pickle will need to be regenerated with both scopes or we just use a new one.
# For simplicity and robust integration, we will assume one token.pickle for the app.

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/drive'
]

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        print("Creds invalid or missing, starting flow...")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token...")
            creds.refresh(Request())
        else:
            print("Starting local server flow...")
            if not os.path.exists('client_secrets.json'):
                raise FileNotFoundError("Error: 'client_secrets.json' not found.")
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("Flow complete, creds obtained.")
        
        print("Saving token.pickle...")
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    print("Building service...")
    try:
        service = build('drive', 'v3', credentials=creds)
        print("Service built successfully.")
        return service
    except Exception as e:
        print(f"Error building service: {e}")
        raise e


def find_or_create_folder(drive_service, folder_name, parent_id=None):
    """
    Finds a folder by name within a parent folder. 
    If not found, creates it.
    """
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    if files:
        print(f"Found folder: {folder_name} ({files[0]['id']})")
        return files[0]['id']
    else:
        print(f"Creating folder: {folder_name}...")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"Created folder: {folder_name} ({folder.get('id')})")
        return folder.get('id')

def upload_file(drive_service, file_path, folder_id, overwrite=False):
    """
    Uploads a file to a specific folder on Google Drive.
    """
    if not os.path.exists(file_path):
        print(f"Skipping upload, file not found: {file_path}")
        return

    file_name = os.path.basename(file_path)
    
    # Get local modification time
    local_mtime = os.path.getmtime(file_path)
    local_mtime_dt = datetime.datetime.fromtimestamp(local_mtime, datetime.timezone.utc)
    # Drive API uses RFC 3339 format, we'll format ours to match (e.g. 2023-10-27T10:00:00.000Z)
    local_mtime_rfc3339 = local_mtime_dt.isoformat(timespec='milliseconds').replace("+00:00", "Z")

    # Check if file already exists in the folder to avoid duplicates
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name, modifiedTime)').execute()
    existing_files = response.get('files', [])
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    if existing_files:
        file_id = existing_files[0]['id']
        drive_mtime_str = existing_files[0].get('modifiedTime')
        
        # If overwrite is False, check if the timestamps differ
        should_update = overwrite
        if not should_update and drive_mtime_str:
            try:
                # Drive timestamps often have .000Z or similar
                # Use fromisoformat for reliable parsing (3.7+)
                drive_mtime_dt = datetime.datetime.fromisoformat(drive_mtime_str.replace('Z', '+00:00'))
                
                # Compare. We use a threshold (e.g. 1 second) to avoid precision issues
                if abs((local_mtime_dt - drive_mtime_dt).total_seconds()) > 1:
                    print(f"File {file_name} has changed locally. Updating Drive version...")
                    should_update = True
            except Exception as e:
                print(f"Warning: Could not compare timestamps for {file_name}: {e}")

        if should_update:
            print(f"File {file_name} already exists. Overwriting content...")
            # Set modifiedTime on Drive to match local
            file_metadata = {'modifiedTime': local_mtime_rfc3339}
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            updated_file = drive_service.files().update(
                fileId=file_id,
                body=file_metadata,
                media_body=media,
                setModifiedTime=True
            ).execute()
            print(f"Updated {file_name} ({updated_file.get('id')})")
            return updated_file.get('id')
        else:
            print(f"File {file_name} already exists and is up to date. Skipping.")
            return file_id

    print(f"Uploading {file_name}...")
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
        'modifiedTime': local_mtime_rfc3339
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_name} ({file.get('id')})")
    return file.get('id')

def upload_episode_assets(campaign_name, episode_name, files_to_upload, root_folder_name="podcasts", files_to_overwrite=None):
    """
    Main function to handle uploading of assets for a specific episode.
    Hierarchy: Root (default="podcasts") -> Campaign -> Episode
    """
    if files_to_overwrite is None:
        files_to_overwrite = set()
    
    try:
        service = get_authenticated_service()
        
        # 1. Resolve/Create Root Folder
        root_folder_id = find_or_create_folder(service, root_folder_name)
        
        # 2. Resolve/Create Campaign Folder inside Root Folder
        campaign_folder_id = find_or_create_folder(service, campaign_name, parent_id=root_folder_id)
        
        # 3. Resolve/Create Episode Folder inside Campaign Folder
        episode_folder_id = find_or_create_folder(service, episode_name, parent_id=campaign_folder_id)
        
        # 4. Upload Files
        for file_path in files_to_upload:
            if file_path:
                should_overwrite = file_path in files_to_overwrite
                upload_file(service, file_path, episode_folder_id, overwrite=should_overwrite)
                
        print("Google Drive upload complete.")
        return True
    except Exception as e:
        print(f"An error occurred during Google Drive upload: {e}")
        return False


