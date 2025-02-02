import openai
import speech_recognition as sr
import pyttsx3
from PIL import Image
import pytesseract
import os

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

def extract_text_from_image():
    image_path = input("Enter the image file path (or press Enter to skip): ").strip()
    if not image_path:
        return ""
    
    if not os.path.exists(image_path):
        print("Invalid file path. Skipping image processing.")
        return ""
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        print("Extracted text from image:", text)
        return text
    except Exception as e:
        print("Error processing image:", str(e))
        return ""

def get_openai_response(prompt, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    api_key = ""
    
    image_text = extract_text_from_image()
    
    while True:
        user_input = recognize_speech_from_mic()
        
        if user_input:
            if "quit" in user_input:
                print("Exiting program...")
                break
            combined_input = image_text + " " + user_input if image_text else user_input
            response = get_openai_response(combined_input, api_key)
            print("AI Response:", response)
            text_to_speech(response)

if __name__ == "__main__":
    main()
