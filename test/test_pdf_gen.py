import os
import json
from scripts import transcript_exporter

def test_pdf_generation():
    # Mock transcription data
    mock_data = {
        "FileName": "test_audio.wav",
        "LengthOfAudio": "00:01:23",
        "Dialog": [
            {"Speaker": "Speaker 1", "Text": "Hello, this is a test."},
            {"Speaker": "Speaker 2", "Text": "I am testing the PDF conversion."}
        ],
        "Topics": [
            {"Start": "00:00:00", "Text": "Introduction"}
        ],
        "Summary": "A test summary of the audio content.",
        "Publications": {
            "YouTube": {
                "Title": "Test Episode",
                "Description": "This is a test description."
            },
            "Facebook": {
                "Post": "This is a test post."
            },
            "Spotify": {
                "Title": "Spotify Test Title",
                "Description": "Spotify test description."
            }
        }
    }
    
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print("Testing transcript export and PDF generation...")
    review_file = transcript_exporter.export_review_document(mock_data, output_dir)
    
    md_path = os.path.join(output_dir, review_file)
    pdf_path = os.path.join(output_dir, review_file.replace(".md", ".pdf"))
    
    if os.path.exists(md_path):
        print(f"SUCCESS: Markdown file created at {md_path}")
    else:
        print(f"FAILURE: Markdown file NOT created at {md_path}")
        
    if os.path.exists(pdf_path):
        print(f"SUCCESS: PDF file created at {pdf_path}")
        print(f"PDF Size: {os.path.getsize(pdf_path)} bytes")
    else:
        print(f"FAILURE: PDF file NOT created at {pdf_path}")

if __name__ == "__main__":
    test_pdf_generation()
