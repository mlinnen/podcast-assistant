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

def get_output_paths(audio_file_path, base_out_dir="out"):
    """Calculates the output directory and JSON path without creating them."""
    folder_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    output_dir = os.path.join(base_out_dir, folder_name)
    json_filename = f"{folder_name}.json"
    json_path = os.path.join(output_dir, json_filename)
    return output_dir, json_path

def create_output_directory(audio_file_path, base_out_dir="out"):
    """Creates an output directory named after the audio file."""
    output_dir, _ = get_output_paths(audio_file_path, base_out_dir)
    
    if not os.path.exists(base_out_dir):
        os.makedirs(base_out_dir)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    return output_dir

def save_results(output_dir, audio_file_path, data):
    """Saves the JSON result and copies the audio file to the output directory."""
    # Copy audio file only if it's not already in the output directory
    dest_path = os.path.join(output_dir, os.path.basename(audio_file_path))
    
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
        shutil.copy2(audio_file_path, output_dir)
    
    # Save JSON
    json_filename = os.path.splitext(os.path.basename(audio_file_path))[0] + ".json"
    json_path = os.path.join(output_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return json_path
