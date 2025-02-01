import openai
import base64
import os
from dotenv import load_dotenv
import pyttsx3
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def imagewa():
    



    def describe_image_four_words(image_path, rate=120):
        """Describes an image in four words or less and speaks it."""

        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in four words or less."},  # Specific prompt
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                        ]
                    }
                ],
                max_tokens=10,  # Limit tokens for a short response
            )

            description = response["choices"][0]["message"]["content"].strip()

            # Split the description into words and take the first four (or fewer)
            words = description.split()
            short_description = " ".join(words[:4])  # Join the first four words

            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.say(short_description)
            engine.runAndWait()

            return short_description

        except Exception as e:
            return f"Error analyzing image: {e}"


    if __name__ == "__main__":
        image_path = input("Enter the path to your image: ")
        speaking_speed = 130

        if os.path.exists(image_path):
            description = describe_image_four_words(image_path, rate=speaking_speed)
            print("Description:", description)
        else:
            print(f"Error: Image not found at {image_path}")
        
imagewa()