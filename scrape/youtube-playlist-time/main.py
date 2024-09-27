import requests
from bs4 import BeautifulSoup
import re
import yt_dlp

# Define proxy settings
proxies = {
    'http': 'http://26.26.26.1:8080',
    'https': 'http://26.26.26.1:80800'
}

# Define URL and headers for the request
url = 'https://www.youtube.com/playlist?list=PLn6x5AfnPjyaD55yuz8rSFcD2GvTIvGsy'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def get_playlist_page(url):
    global headers, proxies
    response = requests.get(url, headers=headers, proxies=proxies)
    response.raise_for_status()
    return response.text


def get_playlist_videos(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',  # Only get video metadata, not the actual video
        'skip_download': True,
        'proxy': proxies['http']
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info['entries']


def sum_durations(videos):
    total_seconds = 0

    for video in videos:
        duration = video.get('duration')
        if duration:
            total_seconds += duration

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}h {minutes}m {seconds}s'


def main(url):
    videos = get_playlist_videos(url)
    total_duration = sum_durations(videos)
    print(f'Total duration of the playlist: {total_duration}')


if __name__ == "__main__":
    main(url)
