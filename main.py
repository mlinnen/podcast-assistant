import argparse
import os
import sys
import json
from datetime import datetime
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
    parser.add_argument("--file", help="Path to the audio file")
    parser.add_argument("--speakers", type=int, default=2, help="Expected number of speakers")
    parser.add_argument("--api-key", help="Google API Key (optional if GOOGLE_API_KEY env var is set)")
    parser.add_argument("--model", default="gemini-3-flash-preview", help="Gemini model to use")
    parser.add_argument("--video", help="Path to an image file to create a video from the audio")
    parser.add_argument("--publish", action="store_true", help="Publish the generated video to YouTube")
    parser.add_argument("--force-marketing", action="store_true", help="Force re-generation of marketing content")
    parser.add_argument("--link", action="append", help="Custom link to add to YouTube description (format: 'URL|Label')")
    parser.add_argument("--hashtag", action="append", help="Custom hashtag to add to YouTube description (overrides generated tags)")
    parser.add_argument("--upload-drive", action="store_true", help="Upload valid output files to Google Drive")
    parser.add_argument("--drive-root", default="podcasts", help="Root folder name on Google Drive (default: 'podcasts')")
    parser.add_argument("-c", "--campaign", help="Optional campaign name to group output files")





    parser.add_argument("-e", "--episode", help="Optional episode name for subfolder under campaign")
    
    args = parser.parse_args()
    
    if not args.file and not args.campaign:
        print("Error: Either --file or --campaign must be provided.")
        parser.print_help()
        sys.exit(1)

    # Handle standalone campaign/episode creation
    if args.campaign and not args.file:
        if args.episode:
            print(f"Initializing directories for campaign: {args.campaign}, episode: {args.episode}")
            episode_dir = file_ops.ensure_episode_directory(args.campaign, args.episode)
            print(f"Success! Episode directory ensured at {episode_dir}")
        else:
            print(f"Initializing directories for campaign: {args.campaign}")
            campaign_dir = file_ops.ensure_campaign_directories(args.campaign)
            print(f"Success! Campaign directory ensured at {campaign_dir}")
        sys.exit(0)

    # Resolve API Key
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Google API Key is required. Provide it via --api-key or GOOGLE_API_KEY environment variable.")
        sys.exit(1)
        
    audio_path = os.path.abspath(args.file)
    original_audio_path = audio_path  # Store original path for video resolution
    
    # Artifact-relative resolution
    if not os.path.exists(audio_path) and args.campaign and args.episode:
        filename = os.path.basename(args.file)
        # Check in the campaign/episode folder directly
        artifacts_dir = os.path.join("out", args.campaign, args.episode)
        candidate_path = os.path.abspath(os.path.join(artifacts_dir, filename))
        if os.path.exists(candidate_path):
            print(f"File not found at literal path, found in episode folder: {candidate_path}")
            audio_path = candidate_path

    # Video artifact-relative resolution
    if args.video:
        video_image_path = os.path.abspath(args.video)
        
        # First, check in the same directory as the ORIGINAL (unresolved) audio file
        if not os.path.exists(video_image_path):
            filename = os.path.basename(args.video)
            original_audio_dir = os.path.dirname(original_audio_path)
            candidate_path = os.path.abspath(os.path.join(original_audio_dir, filename))
            if os.path.exists(candidate_path):
                print(f"Video image not found at literal path, found in original audio folder: {candidate_path}")
                args.video = candidate_path
        
        # Second, check in the same directory as the RESOLVED audio file (if different)
        video_image_path = os.path.abspath(args.video)
        if not os.path.exists(video_image_path) and audio_path != original_audio_path:
            filename = os.path.basename(args.video)
            audio_dir = os.path.dirname(audio_path)
            candidate_path = os.path.abspath(os.path.join(audio_dir, filename))
            if os.path.exists(candidate_path):
                print(f"Video image found in resolved audio folder: {candidate_path}")
                args.video = candidate_path
        
        # Third, check in the campaign/episode output folder
        video_image_path = os.path.abspath(args.video)
        if not os.path.exists(video_image_path) and args.campaign and args.episode:
            filename = os.path.basename(args.video)
            artifacts_dir = os.path.join("out", args.campaign, args.episode)
            candidate_path = os.path.abspath(os.path.join(artifacts_dir, filename))
            if os.path.exists(candidate_path):
                print(f"Video image found in episode output folder: {candidate_path}")
                args.video = candidate_path

    if not os.path.exists(audio_path):
        print(f"Error: File not found at {audio_path}")
        sys.exit(1)
        
    print(f"Processing {audio_path}...")
    if args.campaign:
        print(f"Campaign: {args.campaign}")
    if args.episode:
        print(f"Episode: {args.episode}")
    print(f"Model: {args.model}")
    print(f"Speakers: {args.speakers}")
    
    try:
        # Determine output paths
        output_dir, json_path = file_ops.get_output_paths(audio_path, campaign=args.campaign, episode=args.episode)
        
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


        # Capture Run Metadata
        run_params = vars(args).copy()
        # Remove sensitive data if present
        if 'api_key' in run_params:
            del run_params['api_key']
        
        final_output["RunMetaData"] = {
            "ExecutionTime": datetime.now().isoformat(),
            "Parameters": run_params
        }

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
        existing_publications = final_output.get("Publications", {})
        has_marketing = all(k in existing_publications for k in marketing_keys)
        
        # Check if YouTube data is in the old format (missing structured fields)
        is_old_youtube_format = False
        if "YouTube" in existing_publications:
            if "ShortDescription" not in existing_publications["YouTube"]:
                is_old_youtube_format = True
        
        if args.force_marketing or not has_marketing or is_old_youtube_format:
            if args.force_marketing:
                print("Force-generating marketing content...")
            elif is_old_youtube_format:
                print("Old YouTube format detected. Re-generating marketing content...")
            else:
                print("Generating marketing content...")

            # Process custom links if provided
            custom_links = []
            if args.link:
                for link_arg in args.link:
                    if "|" in link_arg:
                        url, label = link_arg.split("|", 1)
                        custom_links.append({"Url": url.strip(), "Label": label.strip()})
                    else:
                        custom_links.append({"Url": link_arg.strip(), "Label": link_arg.strip()})

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
                
                # Add custom links to YouTube data
                if custom_links:
                    if "YouTube" in final_output["Publications"]:
                        final_output["Publications"]["YouTube"]["CustomLinks"] = custom_links
                
                # Add custom hashtags to YouTube data
                if args.hashtag:
                    if "YouTube" in final_output["Publications"]:
                        # support multiple hashtags in a single flag by splitting on whitespace
                        all_tags = []
                        for tag_arg in args.hashtag:
                            # Remove # and split by whitespace
                            cleaned = tag_arg.replace("#", " ")
                            all_tags.extend(cleaned.split())
                        
                        final_output["Publications"]["YouTube"]["CustomHashtags"] = all_tags

        else:
            print("Skipping marketing content generation (already exists).")

        
        # Create output directory once for all subsequent file operations
        output_dir = file_ops.create_output_directory(audio_path, campaign=args.campaign, episode=args.episode)

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
                        "VideoFile": os.path.basename(video_path),
                        "ImageFile": os.path.basename(args.video)
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
                    youtube_video_id = video_info.get("YouTubeVideoID")
                    
                    proceed_to_publish = True
                    if youtube_video_id:
                        youtube = youtube_publisher.get_authenticated_service()
                        if youtube_publisher.video_exists(youtube, youtube_video_id):
                            confirm = input(f"Video ID '{youtube_video_id}' already exists on YouTube. Overwrite? (y/n): ").lower()
                            if confirm == 'y':
                                if youtube_publisher.delete_video(youtube, youtube_video_id):
                                    # Temporarily remove ID so it triggers a fresh upload below
                                    video_info.pop("YouTubeVideoID", None)
                                else:
                                    print("Failed to delete existing video. Aborting publish.")
                                    proceed_to_publish = False
                            else:
                                print(f"Skipping publication (user chose not to overwrite).")
                                proceed_to_publish = False
                        else:
                            print(f"Video with ID {youtube_video_id} not found on YouTube. Proceeding with fresh upload.")
                            video_info.pop("YouTubeVideoID", None)

                    if proceed_to_publish:
                        print("Publishing to YouTube...")
                        
                        youtube_data = final_output.get("Publications", {}).get("YouTube", {})
                        title = youtube_data.get("Title", "Podcast Episode")
                        
                        # Pass the entire youtube_data dict; youtube_publisher will handle old vs new format
                        video_id = youtube_publisher.publish_video(video_path, title, youtube_data)
                        if video_id:
                            video_info["YouTubeVideoID"] = video_id
                            
                            # Update Facebook post with the new YouTube URL
                            facebook_info = final_output.get("Publications", {}).get("Facebook")
                            if facebook_info and "Post" in facebook_info:
                                youtube_url = f"https://youtu.be/{video_id}"
                                facebook_info["Post"] = facebook_info["Post"].replace("[INSERT YOUTUBE URL HERE]", youtube_url)
                                print(f"Updated Facebook post with URL: {youtube_url}")
                            
                            # Re-export the review document to reflect the updated Facebook post
                            print("Updating review document...")
                            transcript_exporter.export_review_document(final_output, output_dir)
                else:
                    print(f"Warning: Video file not found at {video_path}. Cannot publish.")
            else:
                print("Warning: No video metadata found. Did you use --video?")

        # 9. Save Results
        json_path = file_ops.save_results(output_dir, audio_path, final_output)
        
        print(f"Success! Results saved to {output_dir}")
        print(f"JSON: {json_path}")
        
        # --- Google Drive Upload integration ---
        if args.upload_drive:
            from scripts import drive_uploader
            
            print("\n--- Starting Google Drive Upload ---")
            
            # Determine names for Drive folders
            campaign_name = args.campaign if args.campaign else "DefaultCampaign"
            if args.episode:
                episode_name = args.episode
            else:
                episode_name = os.path.splitext(os.path.basename(audio_path))[0]

            # Identify files to upload
            files_to_upload = []
            
            # 1. Original Audio File
            files_to_upload.append(audio_path)
            
            # 2. Review Documents (MD & PDF)
            if 'review_file' in locals() and review_file:
                md_path = os.path.join(output_dir, review_file)
                files_to_upload.append(md_path) # MD
                
                # PDF (assume same base name)
                pdf_path = os.path.splitext(md_path)[0] + ".pdf"
                if os.path.exists(pdf_path):
                    files_to_upload.append(pdf_path)
            
            # 3. JSON Output
            if 'json_path' in locals() and json_path and os.path.exists(json_path):
                files_to_upload.append(json_path)

            # 4. Images (All in output dir)
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
            if os.path.exists(output_dir):
                for f in os.listdir(output_dir):
                    if os.path.splitext(f)[1].lower() in image_extensions:
                        img_path = os.path.join(output_dir, f)
                        if img_path not in files_to_upload:
                            files_to_upload.append(img_path)

            # 5. Video File
            # Check if video info is in final_output
            if "Publications" in final_output and "Video" in final_output["Publications"]:
                video_filename = final_output["Publications"]["Video"].get("VideoFile")
                if video_filename:
                    video_full_path = os.path.join(output_dir, video_filename)
                    if os.path.exists(video_full_path):
                        files_to_upload.append(video_full_path)
            # Fallback: check based on common naming convention if not in metadata or metadata fails
            else:
                 video_fallback = os.path.join(output_dir, f"{base_name}.mp4")
                 if os.path.exists(video_fallback) and video_fallback not in files_to_upload:
                     files_to_upload.append(video_fallback)

            drive_uploader.upload_episode_assets(campaign_name, episode_name, files_to_upload, root_folder_name=args.drive_root)


        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



if __name__ == "__main__":
    main()

