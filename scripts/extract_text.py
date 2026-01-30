import json
import argparse
import sys

def extract_dialogue_text(json_file_path):
    """
    Reads a transcription JSON file and returns all dialogue text as a single string.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'Dialog' not in data:
            print(f"Error: 'Dialog' key not found in {json_file_path}", file=sys.stderr)
            return None
        
        dialogue_segments = [segment.get('Text', '') for segment in data['Dialog']]
        return " ".join(dialogue_segments)
    
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_file_path}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Extract dialogue text from a transcription JSON file.")
    parser.add_argument("input_file", help="Path to the transcription JSON file")
    
    args = parser.parse_args()
    
    result = extract_dialogue_text(args.input_file)
    if result is not None:
        print(result)

if __name__ == "__main__":
    main()
