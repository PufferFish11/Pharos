from video import detection_mode
from Spoti import music_mode, pause
from image import purchase_mode
#from import jarvis_mode
from mode import select_audio_mode,text_to_speech,record_voice
import speech_recognition as sr
import keyboard


def wait_for_keypress(mode_name):
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:  # Detect key press (not release)
            match mode_name:
                case 'music':
                    pause()
            break



def run_mode(mode_name):
    """Runs the selected mode in a thread and waits for completion"""
    print(f"Starting {mode_name} mode...")

    if "detection" in mode_name.lower():
        detection_mode()
    elif "purchase" in mode_name.lower():
        purchase_mode()
    elif "music" in mode_name.lower():
        text_to_speech("Please select your music by name.")
        while True:
            song_name = record_voice()
            if song_name is None:
                text_to_speech("I couldn't hear you. Please try again.")
                continue
            break;
        music_mode(song_name)
    wait_for_keypress(mode_name)




def main_loop():
    while True:
        selected_mode = select_audio_mode()  # Function to get user input

        run_mode(selected_mode)  # Wait for mode or exit command

        print("Returning to mode selection...")


if __name__ == "__main__":
    main_loop()