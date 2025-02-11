import speech_recognition as sr
import pyttsx3


# Initialize offline TTS engine
tts_engine = pyttsx3.init()

# Enhanced dictionary mapping numbers and words to mode messages
AUDIO_MODES = {
    "detection": "Obstcal detection mode selected.",
    "jarvis": "Podcast mode selected.",
    "purchase": "Movie mode selected.",
    "music": "Music mode selected.",
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
            audio = recognizer.listen(source, phrase_time_limit=5)  # Allow longer input
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
  


def list_audio_modes():
    """ List available modes using TTS. """
    mode_list = "Available audio modes: music, jarvis, detection, purchase."
    text_to_speech(mode_list)



def contains_valid_mode(transcription):
    """ Checks if the transcribed text contains 'one', 'two', or 'three'. """
    valid_keywords = list(AUDIO_MODES.keys())
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
                    return key
        elif mode_selected in ('quit', 'exit', 'bye'):
            return 1         
        else:
            text_to_speech("Invalid selection. Please try again.")
            continue



# Run the voice-based UI
if __name__ == "__main__":

    selected_mode = select_audio_mode()


    
    print(f"🎧 Final Selected Mode: {selected_mode}")
