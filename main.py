from video import detection_mode
from Spoti import music_mode
from image import buyer_mode
#from import jarvis_mode
from mode import select_audio_mode,text_to_speech,record_voice
import speech_recognition as sr


def run_mode(mode_name):
    """Runs the selected mode in a thread and waits for completion"""
    print(f"Starting {mode_name} mode...")
    text_to_speech("Please select your music by name.")

    if "detection" in mode_name.lower():
        detection_mode()
    elif "buyer" in mode_name.lower():
        buyer_mode()
    elif "music" in mode_name.lower():
        while True:
            song_name = record_voice()
            if song_name is None:
                text_to_speech("I couldn't hear you. Please try again.")
                continue
            break;
        music_mode(song_name)
    else:
        print(f"Mode '{mode_name}' not recognized.")
        return



def main_loop():
    while True:
        selected_mode = select_audio_mode()  # Function to get user input
        while True:
            run_mode(selected_mode)  # Wait for mode or exit command

        print("Returning to mode selection...")


if __name__ == "__main__":
    main_loop()