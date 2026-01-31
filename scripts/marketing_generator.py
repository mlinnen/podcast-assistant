from google import genai
from google.genai import types
import json
import typing_extensions as typing

class YouTubeMarketing(typing.TypedDict):
    Title: str
    Description: str

class FacebookMarketing(typing.TypedDict):
    Post: str

class MarketingContent(typing.TypedDict):
    YouTube: YouTubeMarketing
    Facebook: FacebookMarketing

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
    - Topics: A section titled "Topics:" followed by a bulleted list of topics with their "Start" timestamps from the provided topics below. This should come BEFORE the URLs.
    - URLs: Any URLs mentioned in the text MUST be extracted and listed at the end of the description as a bulleted list.
    - Hashtags: 3-5 relevant hashtags after the URLs list.
    
    FACEBOOK REQUIREMENTS:
    - Post: A compelling post for Facebook.
    - IMPORTANT: Do NOT include any URLs in the Facebook post.
    - Focus on engagement and storytelling.
    - Include 2-3 relevant hashtags at the end.
    
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
    
    return json.loads(response.text)
