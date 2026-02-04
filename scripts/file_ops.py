import os
import shutil
import json
from datetime import datetime

def get_file_metadata(file_path):
    """Encapsulates file metadata extraction."""
    stats = os.stat(file_path)
    return {
        "FileName": os.path.basename(file_path),
        "FileExtension": os.path.splitext(file_path)[1],
        "DateCreated": datetime.fromtimestamp(stats.st_ctime).isoformat(),
        "DateModified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "FileSize": stats.st_size
    }

def get_output_paths(audio_file_path, base_out_dir="out", campaign=None, episode=None):
    """Calculates the output directory and JSON path without creating them."""
    
    if campaign:
        if episode:
            # Use episode as the leaf folder if provided
            output_dir = os.path.join(base_out_dir, campaign, episode)
        else:
            # Otherwise use the filename as the leaf folder
            folder_name = os.path.splitext(os.path.basename(audio_file_path))[0]
            output_dir = os.path.join(base_out_dir, campaign, folder_name)
    else:
        folder_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        output_dir = os.path.join(base_out_dir, folder_name)
        
    # JSON file is always named after the audio file (or episode if no audio file yet?)
    # Actually, if we have an audio file, we use its name.
    if audio_file_path:
        json_filename = os.path.splitext(os.path.basename(audio_file_path))[0] + ".json"
    elif episode:
        json_filename = f"{episode}.json"
    else:
        json_filename = "data.json"

    json_path = os.path.join(output_dir, json_filename)
    return output_dir, json_path

def create_output_directory(audio_file_path, base_out_dir="out", campaign=None, episode=None):
    """Creates an output directory for an episode or campaign."""
    output_dir, _ = get_output_paths(audio_file_path, base_out_dir, campaign, episode)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    
    return output_dir

def ensure_campaign_directories(campaign, base_out_dir="out"):
    """Ensures that the campaign base output directory exists."""
    campaign_dir = os.path.join(base_out_dir, campaign)
    if not os.path.exists(campaign_dir):
        os.makedirs(campaign_dir)
    return campaign_dir

def ensure_episode_directory(campaign, episode, base_out_dir="out"):
    """Ensures that the episode directory exists under the campaign, including subfolders."""
    campaign_dir = ensure_campaign_directories(campaign, base_out_dir)
    episode_dir = os.path.join(campaign_dir, episode)
    if not os.path.exists(episode_dir):
        os.makedirs(episode_dir)
    
    return episode_dir

def save_results(output_dir, audio_file_path, data):
    """Saves the JSON result and copies the audio file to the output directory."""
    dest_dir = output_dir

    # Copy audio file only if it's not already in the destination directory
    dest_path = os.path.join(dest_dir, os.path.basename(audio_file_path))
    
    # Use os.path.samefile if both exist, otherwise compare absolute paths
    is_same = False
    if os.path.exists(audio_file_path) and os.path.exists(dest_path):
        try:
            is_same = os.path.samefile(audio_file_path, dest_path)
        except (AttributeError, OSError):
            is_same = os.path.abspath(audio_file_path).lower() == os.path.abspath(dest_path).lower()
    else:
        is_same = os.path.abspath(audio_file_path).lower() == os.path.abspath(dest_path).lower()

    if not is_same:
        shutil.copy2(audio_file_path, dest_dir)
    
    # Save JSON
    json_filename = os.path.splitext(os.path.basename(audio_file_path))[0] + ".json"
    json_path = os.path.join(output_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return json_path
