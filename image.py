from openai import OpenAI
from mode import text_to_speech
import base64
import os
from dotenv import load_dotenv



def purchase_mode(image_path='captured.png'):
    """Gets essential info (name, price, availability) in a few words."""
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = client.chat.completions.create(model="gpt-4o-mini",
        
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Give the object name, estimated price (or range), and where it's typically found (e.g., online, specific store types) in a very concise phrase (under 10 words if possible)."},  # Very specific prompt
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ]
            }
        ],
        max_tokens=20)

        info = response.choices[0].message.content.strip()
        text_to_speech(info)

        
    except Exception as e:
        return f"Error: {e}"


