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

def create_output_directory(base_out_dir="out"):
    """Creates a timestamped output directory."""
    if not os.path.exists(base_out_dir):
        os.makedirs(base_out_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_out_dir, timestamp)
    os.makedirs(output_dir)
    return output_dir

def save_results(output_dir, audio_file_path, data):
    """Saves the JSON result and copies the audio file to the output directory."""
    # Copy audio file
    shutil.copy2(audio_file_path, output_dir)
    
    # Save JSON
    json_filename = os.path.splitext(os.path.basename(audio_file_path))[0] + ".json"
    json_path = os.path.join(output_dir, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return json_path
