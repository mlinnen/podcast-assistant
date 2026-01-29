from google import genai
from google.genai import types
import os
import json
import typing_extensions as typing

class DialogEntry(typing.TypedDict):
    Speaker: str
    Start: str
    Stop: str
    Text: str
    Emotion: str
    PrimaryEmotion: str
    Language: str

class TranscriptionResult(typing.TypedDict):
    LengthOfAudio: str
    Speakers: list[str]
    Dialog: list[DialogEntry]
    Summary: str

def transcribe_audio(audio_file_path, api_key, num_speakers, model_name="gemini-3-flash-preview"):
    """
    Transcribes audio using Google Gemini API (google-genai SDK).
    Returns a dictionary matching the TranscriptionResult structure.
    """
    client = genai.Client(api_key=api_key)
    
    # Upload the file
    audio_file = client.files.upload(file=audio_file_path)
    
    prompt = f"""
    Analyze this audio file.
    It is expected to have {num_speakers} speakers.
    
    Provide a transcription in JSON format with the following structure:
    {{
        "LengthOfAudio": "Duration of the audio file in HH:MM:SS",
        "Speakers": ["List of unique speaker names, e.g., Speaker 1, Speaker 2"],
        "Dialog": [
            {{
                "Speaker": "Speaker Name",
                "Start": "HH:MM:SS",
                "Stop": "HH:MM:SS",
                "Text": "Transcribed text including [non-verbal sounds like laughter]",
                "Emotion": "Specific emotion for this segment (e.g., Laughing, Serious, Excited)",
                "PrimaryEmotion": "The dominant emotion of this specific segment (e.g., Joy, Anger, Neutral)",
                "Language": "Language code (e.g., en-US, es-ES)"
            }}
        ],
        "Summary": "A brief summary of the entire conversation."
    }}
    
    Ensure the "Dialog" list is chronological.
    Identify non-verbal cues like [laughter] in the Text field as well.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, audio_file],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TranscriptionResult
        )
    )
    
    # The SDK parses specific types if response_schema is provided in a certain way, 
    # but with TypedDict it usually returns the string.
    # However, for safety with this new SDK, let's just parse the text.
    # If the SDK automatically parses it into a dict/object, response.parsed might exist?
    # Let's rely on json.loads(response.text) which is standard for JSON mode.
    
    return json.loads(response.text)
