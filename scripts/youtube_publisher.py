import os
import pickle
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from scripts import marketing_generator

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            if not os.path.exists('client_secrets.json'):
                raise FileNotFoundError("Error: 'client_secrets.json' not found. Please provide it in the root directory.")
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)

def publish_video(video_path, title, description_or_youtube_data, category_id="26", privacy_status="unlisted"):
    """
    Uploads a video to YouTube.
    Default category is 26 (How-to & Style).
    Default privacy is unlisted.
    
    Args:
        video_path: Path to the video file
        title: Video title
        description_or_youtube_data: Either a string description (old format) or dict with YouTube data (new format)
        category_id: YouTube category ID
        privacy_status: Video privacy status
    """
    # Assemble description if structured data is provided
    if isinstance(description_or_youtube_data, dict):
        description = marketing_generator.assemble_youtube_description(description_or_youtube_data)
    else:
        description = description_or_youtube_data
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return None

    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    print(f"Uploading file: {video_path}...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")

    print(f"Video id '{response['id']}' was successfully uploaded.")
    return response['id']

def video_exists(youtube, video_id):
    """
    Checks if a video exists on YouTube by its ID.
    """
    try:
        request = youtube.videos().list(
            part="id",
            id=video_id
        )
        response = request.execute()
        return len(response.get('items', [])) > 0
    except Exception:
        return False

def delete_video(youtube, video_id):
    """
    Deletes a video from YouTube by its ID.
    """
    try:
        print(f"Deleting video with ID: {video_id}...")
        youtube.videos().delete(id=video_id).execute()
        print("Video successfully deleted.")
        return True
    except Exception as e:
        print(f"Error deleting video: {e}")
        return False
