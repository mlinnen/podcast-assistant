from google import genai
from google.genai import types
import json
import typing_extensions as typing

class Topic(typing.TypedDict):
    Start: str
    Text: str

class TopicList(typing.TypedDict):
    Topics: list[Topic]

def identify_topics(dialog_data, api_key, model_name="gemini-3-flash-preview"):
    """
    Identifies general topics from dialog entries using Gemini.
    """
    client = genai.Client(api_key=api_key)
    
    # We pass the relevant parts of the dialog to Gemini to identify topics
    # We only need Start and Text for the model to understand the flow and timing
    minified_dialog = [
        {"Start": d.get("Start"), "Text": d.get("Text")} 
        for d in dialog_data
    ]
    
    prompt = f"""
    Analyze the following dialogue from a podcast transcription.
    Identify the key topics discussed throughout the conversation.
    For each topic, provide the "Start" time (from the dialogue) and a brief "Text" description of the topic.
    
    Dialogue:
    {json.dumps(minified_dialog, indent=2)}
    
    Provide the output in JSON format with the following structure:
    {{
        "Topics": [
            {{
                "Start": "HH:MM:SS",
                "Text": "Topic description"
            }}
        ]
    }}
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TopicList
        )
    )
    
    try:
        result = json.loads(response.text)
        return result.get("Topics", [])
    except Exception as e:
        print(f"Error parsing topic analysis: {e}")
        return []
