import requests
from io import BytesIO
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import time
import pygame
from bs4 import BeautifulSoup


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
        # Initialize pygame mixer
        pygame.mixer.init()
        self.is_playing = False

    def play_stream_from_url(self, url):
        # Fetch the audio data from the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Load the audio data into a BytesIO object
            audio_data = BytesIO(response.content)

            # Initialize the pygame mixer
            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()
            self.is_playing = True
            print("Playing music...")
        else:
            print(f"Failed to retrieve audio. Status code: {
                  response.status_code}")

    def stop(self):
        # Stop the playback using pygame's built-in stop functionality
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            print("Music stopped.")
        else:
            print("No music is playing.")


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
    print('sheet')
    player.stop()
    sys.exit(0)


def file_download_detected_action():
    global url
    with open('/home/mahdi/Documents/mini-projects/scrape/playmusic/liked_music', 'a') as file:
        file.write(url + '\n')


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
        'like': file_download_detected_action
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
