import os
from scripts import md_to_pdf

def export_review_document(transcription_data, output_dir):
    """
    Exports a formatted transcript review document (.md) to the output directory.
    Includes dialogue as 'Speaker: Text' and marketing publications at the end.
    """
    file_name_base = os.path.splitext(transcription_data.get("FileName", "transcript"))[0]
    output_filename = f"{file_name_base}_review.md"
    output_path = os.path.join(output_dir, output_filename)
    
    lines = []
    lines.append(f"# Transcript Review: {transcription_data.get('FileName', 'Unknown')}")
    lines.append(f"**Length**: {transcription_data.get('LengthOfAudio', 'Unknown')}  ")
    
    summary = transcription_data.get("Summary")
    if summary:
        lines.append(f"**Summary**: {summary}  ")
    
    lines.append("\n")
    
    # Add Video Link/Info at the beginning
    video_info = transcription_data.get("Publications", {}).get("Video", {})
    if video_info:
        youtube_id = video_info.get("YouTubeVideoID")
        video_file = video_info.get("VideoFile")
        if youtube_id:
            lines.append(f"**YouTube**: [https://youtu.be/{youtube_id}](https://youtu.be/{youtube_id})")
        elif video_file:
            lines.append(f"**Video File**: `{video_file}`")
    
    publications = transcription_data.get("Publications", {})
    if publications:
        lines.append("## Marketing Publications\n")
        
        youtube = publications.get("YouTube", {})
        if youtube:
            lines.append("### YouTube")
            lines.append("This is what will be posted on YouTube\n\n")
            lines.append(f"**Title**:\n\n{youtube.get('Title', 'N/A')}\n\n")
            
            # Check if new structured format or old format
            if "ShortDescription" in youtube:
                # New structured format - show breakdown
                lines.append("**Short Description** (appears before 'show more'):\n\n")
                lines.append(f"{youtube.get('ShortDescription', 'N/A')}\n\n")
                
                lines.append("**Description Body**:\n\n")
                lines.append(f"{youtube.get('DescriptionBody', 'N/A')}\n\n")
                
                topics = youtube.get('Topics', [])
                if topics:
                    lines.append("**Topics**:\n\n")
                    for topic in topics:
                        start = topic.get('Start', '')
                        text = topic.get('Text', '')
                        lines.append(f"- {start} {text}\n")
                    lines.append("\n")
                
                urls = youtube.get('URLs', [])
                custom_links = youtube.get('CustomLinks', [])
                
                if custom_links:
                    lines.append("**URLs** (Custom):\n\n")
                    for link in custom_links:
                        url = link.get('Url', '')
                        label = link.get('Label', '')
                        if label and label != url:
                            lines.append(f"- {label}: {url}\n")
                        else:
                            lines.append(f"- {url}\n")
                    lines.append("\n")
                elif urls:
                    lines.append("**URLs** (Discovered):\n\n")
                    for url in urls:
                        lines.append(f"- {url}\n")
                    lines.append("\n")


                
                hashtags = youtube.get('Hashtags', [])
                if hashtags:
                    lines.append("**Hashtags**:\n\n")
                    hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                    lines.append(f"{hashtag_str}\n\n")
                
                # Also show the final assembled description
                from scripts import marketing_generator
                assembled = marketing_generator.assemble_youtube_description(youtube)
                lines.append("**Final Assembled Description**:\n\n")
                lines.append(f"```\n{assembled}\n```\n\n")
            else:
                # Old format - single description field
                description = youtube.get('Description', 'N/A')
                lines.append(f"**Description**:\n\n{description}\n\n")
            
        facebook = publications.get("Facebook", {})
        if facebook:
            post = facebook.get('Post', 'N/A')
            lines.append("### Facebook")
            lines.append("This is what will be posted on Facebook\n\n")
            lines.append(f"**Description**:\n\n{post}\n\n")

        spotify = publications.get("Spotify", {})
        if spotify:
            description = spotify.get('Description', 'N/A')
            lines.append("### Spotify")
            lines.append("This is what will be posted on Spotify\n\n")
            lines.append(f"**Title**:\n\n{spotify.get('Title', 'N/A')}\n\n")
            lines.append(f"**Description**:\n\n{description}\n\n")

    lines.append("## Transcript\n")
    
    for entry in transcription_data.get("Dialog", []):
        speaker = entry.get("Speaker", "Unknown")
        text = entry.get("Text", "")
        lines.append(f"**{speaker}**: {text}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    # Generate PDF version
    pdf_path = os.path.join(output_dir, f"{file_name_base}_review.pdf")
    md_to_pdf.convert_md_to_pdf(output_path, pdf_path)
    
    return output_filename
