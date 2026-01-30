from google import genai
import os
from dotenv import load_dotenv

def list_gemini_models(api_key=None):
    """
    Lists the available Gemini models using the google-genai SDK.
    """
    if not api_key:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment or provided.")
        return

    client = genai.Client(api_key=api_key)
    
    print(f"{'Model Name':<40} {'Capabilities'}")
    print("-" * 60)
    
    try:
        # list() returns an iterator of Model objects
        for model in client.models.list():
            # The model object has attributes like name, base_model_id, etc.
            # Let's use name and display_name if available
            name = getattr(model, 'name', 'N/A')
            display_name = getattr(model, 'display_name', 'N/A')
            print(f"{name:<40} {display_name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_gemini_models()
