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
    CustomHashtags: typing.NotRequired[list[str]]



class FacebookMarketing(typing.TypedDict):
    Post: str
    Hashtags: list[str]
    CustomHashtags: typing.NotRequired[list[str]]
    YouTubeURL: typing.NotRequired[str]

class SpotifyMarketing(typing.TypedDict):
    Title: str
    Description: str
    Hashtags: list[str]
    CustomHashtags: typing.NotRequired[list[str]]

class MarketingContent(typing.TypedDict):
    YouTube: YouTubeMarketing
    Facebook: FacebookMarketing
    Spotify: SpotifyMarketing

def generate_marketing_content(text, api_key, topics=None, model_name="gemini-3-flash-preview"):
    """
    Generates YouTube, Facebook, and Spotify marketing content using Gemini.
    """
    client = genai.Client(api_key=api_key)
    
    topics_context = ""
    if topics:
        topics_json = json.dumps(topics, indent=2)
        topics_context = f"\n    TOPICS DISCUSSED (with timestamps):\n    {topics_json}\n"

    prompt = f"""
    You are a world-class marketing expert specializing in social media growth and SEO.
    
    Based on the following transcript text and identified topics, generate marketing content for YouTube, Facebook, and Spotify.
    
    YOUTUBE REQUIREMENTS:
    - Title: Catchy, attention-grabbing, and optimized for search.
    - ShortDescription: A brief hook (1-2 sentences) that summarizes the content. This appears before the "Show more" button on YouTube.
    - DescriptionBody: A detailed, compelling summary with proper formatting. Use literal '\\n' characters for line breaks.
    - Topics: An array of topic objects, each with "Start" (timestamp) and "Text" (topic description) fields. Use the provided topics array below as the source.
    - URLs: An array of all URLs mentioned in the transcript. Each URL MUST be prefixed with 'https://' (e.g., https://google.com). If no URLs are mentioned, return an empty array.
    - Hashtags: An array of 3-5 relevant hashtags (without the # symbol, just the text).
    
    FACEBOOK REQUIREMENTS:
    - Post: A compelling post for Facebook. Focus on engagement and storytelling.
    - IMPORTANT: Do NOT include any actual URLs extracted from the text in the Facebook post.
    - IMPORTANT: Do NOT include hashtags in the 'Post' field.
    - IMPORTANT: Do NOT include the YouTube URL placeholder in the 'Post' field.
    - IMPORTANT: Use literal '\\n' characters to create line breaks and separate sections.
    - IMPORTANT: Avoid using em-dashes (—) or extra dashes between words. Use standard punctuation (commas, periods, or colons) instead.
    - Hashtags: An array of 2-3 relevant hashtags (without the # symbol, just the text).
    
    SPOTIFY REQUIREMENTS:
    - Title: Use the exact same title as the YouTube Title.
    - Description: A detailed and professional show notes summary.
    - IMPORTANT: Do NOT include hashtags in the 'Description' field.
    - Include topics (using a hyphen '-' as the bullet point for each item) and any relevant links.
    - IMPORTANT: Use literal '\\n' characters to create line breaks.
    - Hashtags: An array of 3-5 relevant hashtags (without the # symbol, just the text).
    
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
            "Post": "...",
            "Hashtags": ["Keyword1", "Keyword2"]
        }},
        "Spotify": {{
            "Title": "...",
            "Description": "...",
            "Hashtags": ["Keyword1", "Keyword2", "Keyword3"]
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
    
    # Precedence: If custom links are provided, use them EXCLUSIVELY.
    # Otherwise, fall back to discovered URLs.
    if custom_links:
        parts.append("URLs:")
        for link in custom_links:
            url = link.get("Url", "")
            label = link.get("Label", "")
            if label and label != url:
                parts.append(f"- {label}: {url}")
            else:
                parts.append(f"- {url}")
        parts.append("")  # Blank line
    elif urls:
        parts.append("URLs:")
        for url in urls:
            parts.append(f"- {url}")
        parts.append("")  # Blank line


    
    # Hashtags
    hashtags = youtube_data.get("Hashtags", [])
    custom_hashtags = youtube_data.get("CustomHashtags", [])
    
    # Precedence: If custom hashtags are provided, use them EXCLUSIVELY.
    # Otherwise, fall back to discovered hashtags.
    if custom_hashtags:
        hashtag_str = " ".join([f"#{tag}" for tag in custom_hashtags])
        parts.append(hashtag_str)
    elif hashtags:
        # Add # symbol to each hashtag
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        parts.append(hashtag_str)

    
    return "\n".join(parts)

def assemble_facebook_post(facebook_data):
    """
    Assembles a formatted Facebook post from structured data.
    """
    parts = []
    
    # Post content
    if facebook_data.get("Post"):
        parts.append(facebook_data["Post"])
        parts.append("")  # Blank line

    # Hashtags
    hashtags = facebook_data.get("Hashtags", [])
    custom_hashtags = facebook_data.get("CustomHashtags", [])
    
    selected_hashtags = custom_hashtags if custom_hashtags else hashtags
    if selected_hashtags:
        hashtag_str = " ".join([f"#{tag}" for tag in selected_hashtags])
        parts.append(hashtag_str)
        parts.append("")  # Blank line
        
    # YouTube URL
    youtube_url = facebook_data.get("YouTubeURL", "[INSERT YOUTUBE URL HERE]")
    parts.append(youtube_url)
    
    return "\n".join(parts)

def assemble_spotify_description(spotify_data):
    """
    Assembles a formatted Spotify description from structured data.
    """
    parts = []
    
    # Description content
    if spotify_data.get("Description"):
        parts.append(spotify_data["Description"])
        parts.append("")  # Blank line

    # Hashtags
    hashtags = spotify_data.get("Hashtags", [])
    custom_hashtags = spotify_data.get("CustomHashtags", [])
    
    selected_hashtags = custom_hashtags if custom_hashtags else hashtags
    if selected_hashtags:
        hashtag_str = " ".join([f"#{tag}" for tag in selected_hashtags])
        parts.append(hashtag_str)
    
    return "\n".join(parts)

