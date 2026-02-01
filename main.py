import argparse
import os
import sys
import json
from dotenv import load_dotenv
from scripts import transcriber
from scripts import file_ops
from scripts import extract_text
from scripts import marketing_generator
from scripts import transcript_exporter
from scripts import topic_analyzer
from scripts import video_creator
from scripts import youtube_publisher

# Load environment variables (for API Key if in .env)
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Audio Transcriber CLI using Google Gemini")
    parser.add_argument("--file", required=True, help="Path to the audio file")
    parser.add_argument("--speakers", type=int, default=2, help="Expected number of speakers")
    parser.add_argument("--api-key", help="Google API Key (optional if GOOGLE_API_KEY env var is set)")
    parser.add_argument("--model", default="gemini-3-flash-preview", help="Gemini model to use")
    parser.add_argument("--video", help="Path to an image file to create a video from the audio")
    parser.add_argument("--publish", action="store_true", help="Publish the generated video to YouTube")
    
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
        # Determine output paths
        output_dir, json_path = file_ops.get_output_paths(audio_path)
        
        # Initialize final_output
        final_output = {}
        if os.path.exists(json_path):
            print(f"Found existing JSON at {json_path}. Checking for completed parts...")
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    final_output = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing JSON ({e}). Starting fresh.")
                final_output = {}

        # 1. Get File Metadata
        if not all(k in final_output for k in ["FileName", "FileSize", "DateCreated"]):
            metadata = file_ops.get_file_metadata(audio_path)
            final_output.update(metadata)
        
        # 2. Transcribe
        if "Dialog" not in final_output:
            print("Transcribing audio...")
            transcription_result = transcriber.transcribe_audio(audio_path, api_key, args.speakers, args.model)
            final_output.update(transcription_result)
        else:
            print("Skipping transcription (already exists).")

        # 4. Identify Topics
        if "Topics" not in final_output:
            print("Identifying topics...")
            if "Dialog" in final_output:
                topics = topic_analyzer.identify_topics(final_output["Dialog"], api_key, args.model)
                final_output["Topics"] = topics
        else:
            print("Skipping topic analysis (already exists).")
        
        # 5. Extract Text and Generate Marketing Content
        marketing_keys = ["Facebook", "YouTube"]
        has_marketing = "Publications" in final_output and all(k in final_output["Publications"] for k in marketing_keys)
        
        if not has_marketing:
            print("Generating marketing content...")
            dialogue_text = extract_text.extract_dialogue_from_data(final_output)
            if dialogue_text:
                marketing_content = marketing_generator.generate_marketing_content(
                    dialogue_text, 
                    api_key, 
                    topics=final_output.get("Topics"),
                    model_name=args.model
                )
                if "Publications" not in final_output:
                    final_output["Publications"] = {}
                final_output["Publications"].update(marketing_content)
        else:
            print("Skipping marketing content generation (already exists).")
        
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
        
        # 7. Create Video (if requested)
        if args.video:
            # Check if video already exists in Publications
            video_exists = False
            if "Publications" in final_output and "Video" in final_output["Publications"]:
                video_filename = final_output["Publications"]["Video"].get("VideoFile")
                if video_filename and os.path.exists(os.path.join(output_dir, video_filename)):
                    video_exists = True
            
            if not video_exists:
                print("Creating video...")
                video_path = video_creator.create_video(audio_path, args.video, output_dir)
                if video_path:
                    if "Publications" not in final_output:
                        final_output["Publications"] = {}
                    final_output["Publications"]["Video"] = {
                        "VideoFile": os.path.basename(video_path)
                    }
            else:
                print("Skipping video creation (already exists).")

        # 8. Publish to YouTube (if requested)
        if args.publish:
            video_info = final_output.get("Publications", {}).get("Video")
            if video_info and "VideoFile" in video_info:
                video_filename = video_info["VideoFile"]
                video_path = os.path.join(output_dir, video_filename)
                
                if os.path.exists(video_path):
                    # Check if already published
                    if "YouTubeVideoID" not in video_info:
                        print("Publishing to YouTube...")
                        
                        youtube_data = final_output.get("Publications", {}).get("YouTube", {})
                        title = youtube_data.get("Title", "Podcast Episode")
                        description = youtube_data.get("Description", "").replace("\\n", "\n")
                        
                        video_id = youtube_publisher.publish_video(video_path, title, description)
                        if video_id:
                            video_info["YouTubeVideoID"] = video_id
                    else:
                        print(f"Skipping publication (already published with ID: {video_info['YouTubeVideoID']}).")
                else:
                    print(f"Warning: Video file not found at {video_path}. Cannot publish.")
            else:
                print("Warning: No video metadata found. Did you use --video?")

        # 9. Save Results
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
