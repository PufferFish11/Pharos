import openai
import cv2
import numpy as np
import os
import time
import speech_recognition as sr
from playsound import playsound
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to capture image from the webcam
def capture_image():
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    ret, frame = cap.read()  # Capture a single frame
    if ret:
        image_path = "captured_image.jpg"
        cv2.imwrite(image_path, frame)  # Save the image
        cap.release()
        cv2.destroyAllWindows()
        return image_path
    else:
        print("Error: Could not capture image.")
        cap.release()
        cv2.destroyAllWindows()
        return None

# Function to record voice input and convert to text using Whisper
def record_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print("🎤 Say something...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    print("⏳ Processing speech...")
    try:
        with open("voice_input.wav", "wb") as f:
            f.write(audio.get_wav_data())  # Save recorded audio
        
        # Use OpenAI Whisper for transcription
        with open("voice_input.wav", "rb") as audio_file:
            transcript_response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return transcript_response["text"]
    
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return None

# Function to analyze the image and return a response in the correct language
def analyze_image(image_path, prompt):
    with open(image_path, "rb") as image_file:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant for blind people, providing detailed visual descriptions."},
                {"role": "user", "content": prompt, "image": image_file}
            ]
        )
    return response["choices"][0]["message"]["content"]

# Function to detect language from text using OpenAI
def detect_language(text):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Detect the language of the following text and return only the language name."},
            {"role": "user", "content": text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

# Function to convert text to speech in the detected language
def text_to_speech(text, language, output_audio="output.mp3"):
    # Set OpenAI TTS model and voice
    voice = "alloy" if language == "English" else "nova"  # Change voice if needed
    
    response = openai.Audio.create(
        model="tts-1",
        input=text,
        voice=voice
    )
    
    with open(output_audio, "wb") as audio_file:
        audio_file.write(response.content)

    return output_audio

# Function to play the generated audio
def play_audio(audio_file):
    playsound(audio_file)

# Main function to integrate everything
def assist_blind_person():
    # Step 1: Capture image
    image_path = capture_image()
    if not image_path:
        print("Failed to capture image.")
        return
    
    # Step 2: Record voice command
    user_prompt = record_voice()
    if not user_prompt:
        print("Failed to process voice input.")
        return
    
    print(f"🗣️ Recognized Speech: {user_prompt}")
    
    # Step 3: Analyze the image with GPT-4 Vision
    description = analyze_image(image_path, user_prompt)
    print(f"📝 Generated Description: {description}")

    # Step 4: Detect language
    detected_language = detect_language(description)
    print(f"🌍 Detected Language: {detected_language}")

    # Step 5: Convert text to speech
    audio_file = text_to_speech(description, detected_language)
    
    # Step 6: Play the audio
    play_audio(audio_file)

# Run the assistant
if __name__ == "__main__":
    assist_blind_person()
