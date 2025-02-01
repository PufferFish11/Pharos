import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

print(CLIENT_SECRET)

SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Search for a song and play it
def play_song_by_name(song_name):
    results = sp.search(q=song_name, type="track", limit=1)
    if results["tracks"]["items"]:
        song_uri = results["tracks"]["items"][0]["uri"]
        song_name = results["tracks"]["items"][0]["name"]
        artist = results["tracks"]["items"][0]["artists"][0]["name"]
        print(f"Playing: {song_name} by {artist}")
        sp.start_playback(uris=[song_uri])
    else:
        print("Song not found!")

# Pause playback
def pause():
    sp.pause_playback()

# Resume playback
def resume():
    sp.start_playback()

# Example usage
if __name__ == "__main__":
    song_name = input("Enter a song name: ")  # User provides a song name
    play_song_by_name(song_name)  # Search and play the song
