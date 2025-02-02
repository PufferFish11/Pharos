import openai
import base64
import os
from dotenv import load_dotenv
import pyttsx3

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def purchase_mode():
    def get_essential_info(image_path, rate=120):
        """Gets essential info (name, price, availability) in a few words."""

        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Give the object name, estimated price (or range), and where it's typically found (e.g., online, specific store types) in a very concise phrase (under 10 words if possible)."},  # Very specific prompt
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                        ]
                    }
                ],
                max_tokens=20,  # Even more restrictive token limit
            )

            info = response["choices"][0]["message"]["content"].strip()

            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.say(info)
            engine.runAndWait()

            return info

        except Exception as e:
            return f"Error: {e}"


    if __name__ == "__main__":
        image_path = input("Enter the path to your image: ")
        speaking_speed = 145

        if os.path.exists(image_path):
            info = get_essential_info(image_path, rate=speaking_speed)
            print("Information (also spoken):", info)
        else:
            print(f"Error: Image not found at {image_path}")
            
