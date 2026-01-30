import os

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
    lines.append(f"Length: {transcription_data.get('LengthOfAudio', 'Unknown')}")
    lines.append("\n## Transcript\n")
    
    for entry in transcription_data.get("Dialog", []):
        speaker = entry.get("Speaker", "Unknown")
        text = entry.get("Text", "")
        lines.append(f"**{speaker}**: {text}\n")
    
    publications = transcription_data.get("Publications", {})
    if publications:
        lines.append("\n---\n")
        lines.append("## Marketing Publications\n")
        
        youtube = publications.get("YouTube", {})
        if youtube:
            description = youtube.get('Description', 'N/A').replace('\\n', '\n')
            lines.append("### YouTube")
            lines.append(f"**Title**: {youtube.get('Title', 'N/A')}")
            lines.append(f"**Description**:\n{description}\n")
            
        facebook = publications.get("Facebook", {})
        if facebook:
            post = facebook.get('Post', 'N/A').replace('\\n', '\n')
            lines.append("### Facebook")
            lines.append(f"**Post**:\n{post}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return output_filename
