import openai
import base64
import os
from dotenv import load_dotenv
import pyttsx3
import speech_recognition as sr
from PIL import Image
import io

print("\n\nI am a dedicated assistant for visually impaired users.")

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError:
        print("Could not request results, check your internet connection.")
        return None


def get_openai_response(prompt, api_key, encoded_image=None):
    openai.api_key = api_key
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    if encoded_image:
        messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Or another suitable model
            messages=messages,
            max_tokens=50  # Reduced max_tokens for shorter responses
        )
        # Extract and strip whitespace, limit to one line
        response_text = response["choices"][0]["message"]["content"].strip()
        return response_text.splitlines()[0] if response_text else "" # Get the first line only
    except openai.error.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return "Error communicating with OpenAI API."
    except Exception as e:
        print(f"An unexpected error occurred with OpenAI: {e}")
        return "An unexpected error occurred with OpenAI."


def encode_image(image_path):
    try:
        img = Image.open(image_path)
        img.thumbnail((512, 512))  # Example: Resize to max 512x512 pixels (adjust as needed)

        # Use BytesIO to store the resized image in memory
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=80) # Save resized image to memory
        img_str = base64.b64encode(buffered.getvalue()).decode() # Encode from memory

        return img_str
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None
    

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def main():
    load_dotenv()

    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    api_key = openai.api_key

    image_path = "/Users/saifshaikh/Desktop/MAIS Code/Pharos/reff.jpg".strip()
    encoded_image = None

    if image_path:
        if not os.path.exists(image_path):
            print(f"Error: File not found at '{image_path}'.")
            return
        encoded_image = encode_image(image_path)
        if not encoded_image:
            return

    while True:
        user_input = recognize_speech_from_mic()

        if user_input:
            if user_input.lower() in ("bye", "quit", "goodbye"):  # Check for exit phrases
                print("Exiting program...")
                break  # Exit the loop

            prompt = user_input.strip()

            if prompt:
                response = get_openai_response(prompt, api_key, encoded_image)
                print("VisHelp response:", response)
                text_to_speech(response)
            else:
                print("No input provided (speech).")
        elif user_input is None: # Handle the case where speech recognition fails
            print("Could not understand audio. Please try again.")
            continue # Go to the next iteration of the loop
        else:
          print("No Input Provided")


if __name__ == "__main__":
    main()