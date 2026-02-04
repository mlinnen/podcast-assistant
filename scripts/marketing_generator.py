from google import genai
from google.genai import types
import json
import typing_extensions as typing
import re

def ensure_url_protocol(text):
    """
    Finds URLs in the text that don't have a protocol (e.g., google.com) 
    and adds 'https://' to them.
    """
    # Regex to find potential URLs
    url_pattern = r'\b(?:https?://|www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?'
    
    def replace_url(match):
        url = match.group(0)
        # Skip if it already has a protocol or is an email
        if url.startswith("http://") or url.startswith("https://") or "@" in url:
            return url
        if url.startswith("www."):
            return f"https://{url}"
        return f"https://{url}"

    return re.sub(url_pattern, replace_url, text)

class YouTubeMarketing(typing.TypedDict):
    Title: str
    Description: str

class FacebookMarketing(typing.TypedDict):
    Post: str

class SpotifyMarketing(typing.TypedDict):
    Title: str
    Description: str

class MarketingContent(typing.TypedDict):
    YouTube: YouTubeMarketing
    Facebook: FacebookMarketing
    Spotify: SpotifyMarketing

def generate_marketing_content(text, api_key, topics=None, model_name="gemini-3-flash-preview"):
    """
    Generates YouTube and Facebook marketing content using Gemini.
    """
    client = genai.Client(api_key=api_key)
    
    topics_context = ""
    if topics:
        topics_json = json.dumps(topics, indent=2)
        topics_context = f"\n    TOPICS DISCUSSED (with timestamps):\n    {topics_json}\n"

    prompt = f"""
    You are a world-class marketing expert specializing in social media growth and SEO.
    
    Based on the following transcript text and identified topics, generate marketing content for YouTube and Facebook.
    
    YOUTUBE REQUIREMENTS:
    - YouTubeTitle: Catchy, attention-grabbing, and optimized for search.
    - YouTubeDescription: A brief, compelling summary.
    - IMPORTANT: Use literal '\n' characters to create line breaks and separate sections (e.g., Summary, Topics, URLs, Hashtags).
    - Topics: A section titled "Topics:" followed by a list of topics using a hyphen '-' as the bullet point for each item, with their "Start" timestamps from the provided topics below. This should come BEFORE the URLs.
    - URLs: Any URLs mentioned in the text MUST be extracted and listed at the end of the description as a list using a hyphen '-' as the bullet point for each item. IMPORTANT: Each URL MUST be prefixed with 'https://' (e.g., https://google.com).
    - Hashtags: 3-5 relevant hashtags after the URLs list.
    
    FACEBOOK REQUIREMENTS:
    - Post: A compelling post for Facebook.
    - IMPORTANT: Do NOT include any actual URLs extracted from the text in the Facebook post.
    - Focus on engagement and storytelling.
    - IMPORTANT: Use literal '\n' characters to create line breaks and separate sections (e.g., Summary, Topics, URLs, Hashtags).
    - IMPORTANT: Avoid using em-dashes (—) or extra dashes between words. Use standard punctuation (commas, periods, or colons) instead.
    - Include 2-3 relevant hashtags at the end.
    - AFTER the hashtags, on a new line, add the placeholder text "[INSERT YOUTUBE URL HERE]".
    
    SPOTIFY REQUIREMENTS:
    - Title: Use the exact same title as the YouTube Title.
    - Description: A detailed and professional show notes summary.
    - Include topics (using a hyphen '-' as the bullet point for each item) and any relevant links.
    - IMPORTANT: Use literal '\n' characters to create line breaks.
    
    {topics_context}
    
    TRANSCRIPT TEXT:
    {text}
    
    Provide the output in JSON format with the following structure:
    {{
        "YouTube": {{
            "Title": "...",
            "Description": "..."
        }},
        "Facebook": {{
            "Post": "..."
        }},
        "Spotify": {{
            "Title": "...",
            "Description": "..."
        }}
    }}
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MarketingContent
        )
    )
    
    result = json.loads(response.text)
    
    # Post-process to ensure all URLs have https://
    if "YouTube" in result and "Description" in result["YouTube"]:
        result["YouTube"]["Description"] = ensure_url_protocol(result["YouTube"]["Description"])
    
    if "Spotify" in result and "Description" in result["Spotify"]:
        result["Spotify"]["Description"] = ensure_url_protocol(result["Spotify"]["Description"])
        
    return result
