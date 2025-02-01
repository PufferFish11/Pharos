import pyaudio
import wave
import openai
import os
from dotenv import load_dotenv


def aud():
    load_dotenv()
    # Set your OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Keywords to recognize in English
    keywords = ["photo", "picture", "in front of", "what"]

    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5  # Adjust as needed
    OUTPUT_FILENAME = "recorded_audio.wav"

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Start recording
    print("Recording...")
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                        input=True, frames_per_buffer=CHUNK)
    frames = []

    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a file
    with wave.open(OUTPUT_FILENAME, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    # Open and translate the audio using OpenAI Whisper API
    try:
        with open(OUTPUT_FILENAME, "rb") as audio_file:
            response = openai.Audio.translate("whisper-1", audio_file)

        # Print the translated text in English
        translation = response['text']
        print("Translated Text (to English):", translation)

        # Check for keywords in the translated transcription
        detected_keywords = [kw for kw in keywords if kw in translation.lower()]
        
        if detected_keywords:
            print("Detected Keywords:", ", ".join(detected_keywords))
        else:
            print("No specific keywords detected.")

    except Exception as e:
        print("Error during transcription:", e)

    finally:
        # Clean up: Delete the recorded file (optional)
        os.remove(OUTPUT_FILENAME)

if __name__ == "__main__":
    aud()