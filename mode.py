from openai import OpenAI
import os
import speech_recognition as sr
from playsound import playsound
from dotenv import load_dotenv
import pyaudio
# Define available audio modes
AUDIO_MODES = {
    "mode 1": "Music mode selected. Enjoy high-quality sound.",
    "mode 2": "Podcast mode selected. Enhancing speech clarity.",
    "mode 3": "Movie mode selected. Optimizing for cinematic experience.",
    "mode 4": "Gaming mode selected. Low latency for real-time sound."
}

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to generate speech output and play it
def text_to_speech(text, output_audio="output.mp3"):
    response = client.audio.speech.create(model="tts-1",
    input=text,
    voice="alloy")

    with open(output_audio, "wb") as audio_file:
        audio_file.write(response.content)

    playsound(output_audio)

# Function to record voice input
def record_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Speak now...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    print("⏳ Processing voice input...")
    try:
        # Convert speech to text using SpeechRecognition
        text = recognizer.recognize_google(audio).lower()
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand the audio.")
        return None
    except sr.RequestError:
        print("❌ Could not request results.")
        return None

# Function to list available modes using TTS
def list_audio_modes():
    mode_list = "Available audio modes are: " + ", ".join(AUDIO_MODES.keys()) + ". Please say the mode you want."
    text_to_speech(mode_list)

# Function to confirm the user's choice
def confirm_choice(choice):
    text_to_speech(f"You selected {choice}. Is that correct? Please say Yes or No.")
    while True:
        confirmation = record_voice()
        if confirmation:
            if "yes" in confirmation:
                text_to_speech(f"Confirmed. {AUDIO_MODES[choice]}")
                return True
            elif "no" in confirmation:
                text_to_speech("Okay, please choose again.")
                return False
            else:
                text_to_speech("I didn't understand. Please say Yes or No.")

# Main function to handle voice-based selection
def select_audio_mode():
    while True:
        list_audio_modes()
        mode_selected = record_voice()

        if mode_selected is None:
            text_to_speech("I couldn't hear you. Please try again.")
            continue

        for mode in AUDIO_MODES.keys():
            if mode in mode_selected:
                if confirm_choice(mode):
                    return mode  # Final selection
                else:
                    break  # Loop again for a new choice

# Run the voice-based UI
if __name__ == "__main__":
    selected_mode = select_audio_mode()
    print(f"🎧 Final Selected Mode: {selected_mode}")
