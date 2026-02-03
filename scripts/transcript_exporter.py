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
            description = youtube.get('Description', 'N/A')
            lines.append("### YouTube")
            lines.append("This is what will be posted on YouTube\n\n")
            lines.append(f"**Title**:\n\n{youtube.get('Title', 'N/A')}\n\n")
            lines.append(f"**Description**:\n\n{description}")
            
        facebook = publications.get("Facebook", {})
        if facebook:
            post = facebook.get('Post', 'N/A')
            lines.append("### Facebook")
            lines.append("This is what will be posted on Facebook\n\n")
            lines.append(f"**Description**:\n\n{post}")

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
