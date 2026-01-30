import argparse
import os
import sys
from dotenv import load_dotenv
from scripts import transcriber
from scripts import file_ops
from scripts import extract_text
from scripts import marketing_generator
from scripts import transcript_exporter
from scripts import topic_analyzer

# Load environment variables (for API Key if in .env)
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Audio Transcriber CLI using Google Gemini")
    parser.add_argument("--file", required=True, help="Path to the audio file")
    parser.add_argument("--speakers", type=int, default=2, help="Expected number of speakers")
    parser.add_argument("--api-key", help="Google API Key (optional if GOOGLE_API_KEY env var is set)")
    parser.add_argument("--model", default="gemini-3-flash-preview", help="Gemini model to use")
    
    args = parser.parse_args()
    
    # Resolve API Key
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Google API Key is required. Provide it via --api-key or GOOGLE_API_KEY environment variable.")
        sys.exit(1)
        
    audio_path = os.path.abspath(args.file)
    if not os.path.exists(audio_path):
        print(f"Error: File not found at {audio_path}")
        sys.exit(1)
        
    print(f"Processing {audio_path}...")
    print(f"Model: {args.model}")
    print(f"Speakers: {args.speakers}")
    
    try:
        # 1. Get File Metadata
        metadata = file_ops.get_file_metadata(audio_path)
        
        # 2. Transcribe
        print("Transcribing audio...")
        transcription_result = transcriber.transcribe_audio(audio_path, api_key, args.speakers, args.model)
        
        # 3. Combine Data
        final_output = {
            **metadata,
            **transcription_result
        }

        # 4. Identify Topics
        print("Identifying topics...")
        if "Dialog" in final_output:
            topics = topic_analyzer.identify_topics(final_output["Dialog"], api_key, args.model)
            final_output["Topics"] = topics
        
        # 5. Extract Text and Generate Marketing Content
        print("Generating marketing content...")
        dialogue_text = extract_text.extract_dialogue_from_data(final_output)
        if dialogue_text:
            marketing_content = marketing_generator.generate_marketing_content(dialogue_text, api_key, args.model)
            final_output["Publications"] = marketing_content
        
        # Create output directory once for all subsequent file operations
        output_dir = file_ops.create_output_directory(audio_path)

        # 6. Export Transcript Review Document
        print("Exporting review document...")
        review_file = transcript_exporter.export_review_document(final_output, output_dir)
        
        if "Publications" not in final_output:
            final_output["Publications"] = {}
        final_output["Publications"]["Review"] = {
            "TranscriptFile": review_file
        }
        
        # 7. Save Results
        json_path = file_ops.save_results(output_dir, audio_path, final_output)
        
        print(f"Success! Results saved to {output_dir}")
        print(f"JSON: {json_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
