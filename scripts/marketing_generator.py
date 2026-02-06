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

class TopicEntry(typing.TypedDict):
    Start: str
    Text: str

class CustomLinkEntry(typing.TypedDict):
    Url: str
    Label: str

class YouTubeMarketing(typing.TypedDict):
    Title: str
    ShortDescription: str
    DescriptionBody: str
    Topics: list[TopicEntry]
    URLs: list[str]
    Hashtags: list[str]
    CustomLinks: typing.NotRequired[list[CustomLinkEntry]]


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
    - Title: Catchy, attention-grabbing, and optimized for search.
    - ShortDescription: A brief hook (1-2 sentences) that summarizes the content. This appears before the "Show more" button on YouTube.
    - DescriptionBody: A detailed, compelling summary with proper formatting. Use literal '\n' characters for line breaks.
    - Topics: An array of topic objects, each with "Start" (timestamp) and "Text" (topic description) fields. Use the provided topics array below as the source.
    - URLs: An array of all URLs mentioned in the transcript. Each URL MUST be prefixed with 'https://' (e.g., https://google.com). If no URLs are mentioned, return an empty array.
    - Hashtags: An array of 3-5 relevant hashtags (without the # symbol, just the text).
    
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
            "ShortDescription": "...",
            "DescriptionBody": "...",
            "Topics": [
                {{"Start": "00:00:00", "Text": "..."}},
                {{"Start": "00:05:30", "Text": "..."}}
            ],
            "URLs": ["https://example.com", "https://another.com"],
            "Hashtags": ["Keyword1", "Keyword2", "Keyword3"]
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
    if "YouTube" in result and "URLs" in result["YouTube"]:
        result["YouTube"]["URLs"] = [ensure_url_protocol(url) for url in result["YouTube"]["URLs"]]
    
    if "Spotify" in result and "Description" in result["Spotify"]:
        result["Spotify"]["Description"] = ensure_url_protocol(result["Spotify"]["Description"])
        
    return result

def assemble_youtube_description(youtube_data):
    """
    Assembles a formatted YouTube description from structured data.
    
    Args:
        youtube_data: Dictionary containing YouTube marketing fields (ShortDescription, 
                     DescriptionBody, Topics, URLs, Hashtags)
    
    Returns:
        Formatted description string ready for YouTube
    """
    # Handle both old format (single Description) and new format (structured)
    if "Description" in youtube_data and "ShortDescription" not in youtube_data:
        # Old format - return as-is for backward compatibility
        return youtube_data["Description"]
    
    parts = []
    
    # Short description (appears before "show more")
    if youtube_data.get("ShortDescription"):
        parts.append(youtube_data["ShortDescription"])
        parts.append("")  # Blank line
    
    # Description body
    if youtube_data.get("DescriptionBody"):
        parts.append(youtube_data["DescriptionBody"])
        parts.append("")  # Blank line
    
    # Topics section
    topics = youtube_data.get("Topics", [])
    if topics:
        parts.append("Topics:")
        for topic in topics:
            start = topic.get("Start", "")
            text = topic.get("Text", "")
            parts.append(f"- {start} {text}")
        parts.append("")  # Blank line
    
    # URLs section
    urls = youtube_data.get("URLs", [])
    custom_links = youtube_data.get("CustomLinks", [])
    
    if urls or custom_links:
        parts.append("URLs:")
        # Show custom links first
        for link in custom_links:
            url = link.get("Url", "")
            label = link.get("Label", "")
            if label and label != url:
                parts.append(f"- {label}: {url}")
            else:
                parts.append(f"- {url}")
                
        # Show discovered links
        for url in urls:
            parts.append(f"- {url}")
        parts.append("")  # Blank line

    
    # Hashtags
    hashtags = youtube_data.get("Hashtags", [])
    if hashtags:
        # Add # symbol to each hashtag
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        parts.append(hashtag_str)
    
    return "\n".join(parts)
