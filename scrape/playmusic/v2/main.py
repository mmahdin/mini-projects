import requests
import tempfile
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import time
import pygame
from bs4 import BeautifulSoup
import urllib.parse


class MultiFileCreationHandler(FileSystemEventHandler):
    def __init__(self, file_callbacks):
        # A dictionary that maps file names to their respective callback functions
        self.file_callbacks = file_callbacks

    def on_created(self, event):
        # Loop through all the files and check if the event matches any
        for file_name, callback in self.file_callbacks.items():
            if event.src_path.endswith(file_name):
                print(f"'{file_name}' file detected!")
                callback()  # Call the corresponding function


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        self.current_audio_data = None
        self.playback_position = 0  # To store the playback position in milliseconds
        self.temp_audio_file = None  # To store the temp audio file

    def play_stream_from_url(self, url, start_position=0):
        # Fetch the audio data from the URL if not already fetched
        self.url = url
        if self.current_audio_data is None:
            response = requests.get(url)
            if response.status_code == 200:
                self.current_audio_data = response.content
                # Write the audio data to a temporary file
                self.temp_audio_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3")
                self.temp_audio_file.write(self.current_audio_data)
                self.temp_audio_file.close()
            else:
                print(f"Failed to retrieve audio. Status code: {
                      response.status_code}")
                return

        # Load and play the audio from the temp file, seeking to the start position
        pygame.mixer.music.load(self.temp_audio_file.name)
        # Start from the beginning and manually seek
        pygame.mixer.music.play(start=0)
        pygame.mixer.music.set_pos(start_position / 1000.0)  # Seek in seconds
        self.is_playing = True
        print(f"Resumed music from {start_position / 1000.0} seconds...")

    def stop(self):
        if self.is_playing:
            # Save the current playback position
            self.playback_position = pygame.mixer.music.get_pos()
            pygame.mixer.music.stop()
            self.is_playing = False
            print(f"Music stopped at {self.playback_position} milliseconds.")
        else:
            print("No music is playing.")

    def save_current_audio(self, save_path=f'/home/mahdi/Music/myAppMusic/'):
        if self.current_audio_data:
            save_path = save_path + get_song_info(self.url) + ".mp3"
            with open(save_path, 'wb') as file:
                file.write(self.current_audio_data)
            print(f"Audio saved to {save_path}")
        else:
            print("No audio data available to save.")


def get_song_info(url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)

    # Split the path of the URL
    path_parts = parsed_url.path.split('/')

    # Get the artist and song info from the last part of the URL
    # Replace URL encoded spaces with spaces
    filename = path_parts[-1].replace('%20', ' ')
    song_info = filename.replace('.mp3', '')  # Remove the file extension

    return song_info


def read_and_remove_first_line(file_path='/home/mahdi/Documents/mini-projects/scrape/playmusic/musicList.txt'):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if lines:
        first_line = lines[0].strip()
    else:
        first_line = None

    with open(file_path, 'w') as file:
        file.writelines(lines[1:])

    return first_line


def file_close_detected_action():
    player.stop()
    if player.temp_audio_file:
        os.remove(player.temp_audio_file.name)
    pygame.mixer.quit()
    sys.exit(0)


def file_like_detected_action():
    global url
    with open('/home/mahdi/Documents/mini-projects/scrape/playmusic/liked_music', 'a') as file:
        file.write(url + '\n')


def file_save_detected_action():
    player.save_current_audio()


def file_stop_detected_action():
    if player.is_playing:
        print("Audio is playing. Stopping audio...")
        player.stop()
    else:
        print(f"Audio is stopped. Resuming from {
              player.playback_position} milliseconds...")
        player.play_stream_from_url(url, player.playback_position)


def audio_link(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        pakh = soup.find_all('div', {'class': 'pakh'})[0]
        audio = pakh.find_all('div', {'class': 'audio'})[0]
        audio_tag = audio.find('audio')
        link = audio_tag['src']
        return link


def run():
    with open('/home/mahdi/play_music/close', 'w') as file:
        pass
    os.remove('/home/mahdi/play_music/close')
    global url
    link = audio_link(url)
    print(link)

    path = '/home/mahdi/play_music/'
    file_callbacks = {
        'close': file_close_detected_action,
        'like': file_like_detected_action,
        'save': file_save_detected_action,
        'stop': file_stop_detected_action,
    }

    # Create an event handler for detecting multiple files
    event_handler = MultiFileCreationHandler(file_callbacks)

    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    player.play_stream_from_url(link)

    try:
        # Keep the observer running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()  # Gracefully stop the observer
    observer.join()


player = AudioPlayer()
url = read_and_remove_first_line()
run()
