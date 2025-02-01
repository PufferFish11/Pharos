import speech_recognition as sr
import pyttsx3

# Initialize offline TTS engine
tts_engine = pyttsx3.init()

# Enhanced dictionary mapping numbers and words to mode messages
AUDIO_MODES = {
    "one": "Music mode selected. Enjoy high-quality sound.",
    "two": "Podcast mode selected. Enhancing speech clarity.",
    "three": "Movie mode selected. Optimizing for cinematic experience.",
    "four": "Gaming mode selected. Low latency for real-time sound.",
}

def text_to_speech(text):
    """ Speak the given text using pyttsx3 (Offline TTS). """
    tts_engine.say(text)
    tts_engine.runAndWait()

def record_voice():
    """ Records voice and converts it to text. """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        try:
            print("🎤 Speak now...")
            audio = recognizer.listen(source)  # Allow longer input
        except sr.WaitTimeoutError:
            print("⏳ No speech detected. Please try again.")
            return None

    print("⏳ Processing voice input...")
    try:
        text = recognizer.recognize_google(audio, language="en-US").lower()
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand the audio. Try speaking clearly.")
        return None
    except sr.RequestError as e:
        print(f"❌ Could not connect to Google's recognition service: {str(e)}. Trying offline mode...")

def list_audio_modes():
    """ List available modes using TTS. """
    mode_list = "Available audio modes: One, Two, Three, Four. Please say a number or word."
    text_to_speech(mode_list)

def confirm_choice(choice):
    """ Asks the user to confirm their selection. """
    text_to_speech(f"You selected Mode {choice}. Is that correct? Please say Yes or No.")
    
    while True:
        confirmation = record_voice()
        if confirmation and any(word in confirmation for word in ["yes", "yeah", "yep"]):
            text_to_speech(f"Confirmed. {AUDIO_MODES[choice]}")
            return True
        elif confirmation and any(word in confirmation for word in ["no", "nope", "nah"]):
            text_to_speech("Okay, please choose again.")
            return False
        else:
            text_to_speech("I didn't understand. Please say Yes or No.")

def contains_valid_mode(transcription):
    """ Checks if the transcribed text contains 'one', 'two', or 'three'. """
    valid_keywords = ["one", "two", "three", "four"]
    return any(word in transcription for word in valid_keywords)

def select_audio_mode():
    """ Handles the process of selecting an audio mode via voice input. """
    while True:
        list_audio_modes()
        mode_selected = record_voice()

        if mode_selected is None:
            text_to_speech("I couldn't hear you. Please try again.")
            continue

        if contains_valid_mode(mode_selected):  # Check if transcription contains valid mode
            for key in AUDIO_MODES:
                if key in mode_selected:
                    if confirm_choice(key):
                        return key
        else:
            text_to_speech("Invalid selection. Please say a number between one and four.")
            continue

# Run the voice-based UI
if __name__ == "__main__":
    selected_mode = select_audio_mode()
    print(f"🎧 Final Selected Mode: {selected_mode}")
