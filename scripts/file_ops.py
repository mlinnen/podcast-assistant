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

def create_output_directory(audio_file_path, base_out_dir="out"):
    """Creates an output directory named after the audio file."""
    if not os.path.exists(base_out_dir):
        os.makedirs(base_out_dir)
    
    folder_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    output_dir = os.path.join(base_out_dir, folder_name)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    return output_dir

def save_results(output_dir, audio_file_path, data):
    """Saves the JSON result and copies the audio file to the output directory."""
    # Copy audio file only if it's not already in the output directory
    dest_path = os.path.join(output_dir, os.path.basename(audio_file_path))
    if os.path.abspath(audio_file_path) != os.path.abspath(dest_path):
        shutil.copy2(audio_file_path, output_dir)
    
    # Save JSON
    json_filename = os.path.splitext(os.path.basename(audio_file_path))[0] + ".json"
    json_path = os.path.join(output_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return json_path
