from google import genai
from google.genai import types
import json
import typing_extensions as typing

class MarketingContent(typing.TypedDict):
    YouTubeTitle: str
    YouTubeDescription: str

def generate_marketing_content(text, api_key, model_name="gemini-3-flash-preview"):
    """
    Generates a YouTube title and description using Gemini.
    """
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are a world-class marketing expert specializing in YouTube growth and SEO.
    
    Based on the following transcript text, generate a catchy, high-engagement YouTube Title and a professional YouTube Description.
    
    REQUIRMENTS:
    - The Title should be attention-grabbing and optimized for search.
    - The Description should be a brief, compelling summary of the text.
    - IMPORTANT: Any URLs mentioned in the text MUST be extracted and listed at the end of the description as a bulleted list.
    - The description should use YouTube-friendly formatting (line breaks, clear sections).
    - Generate 3-5 relevant hashtags that match the content. These should come AFTER the URLs list.
    
    TRANSCRIPT TEXT:
    {text}
    
    Provide the output in JSON format with the following keys:
    - "YouTubeTitle"
    - "YouTubeDescription"
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MarketingContent
        )
    )
    
    return json.loads(response.text)
