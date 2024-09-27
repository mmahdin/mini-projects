from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError


def read_music_metadata(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
        metadata = {
            'Title': audio.get('TIT2', 'Unknown'),
            'Artist': audio.get('TPE1', 'Unknown'),
            'Album': audio.get('TALB', 'Unknown'),
            'Release Date': audio.get('TDRC', 'Unknown'),
            'Genre': audio.get('TCON', 'Unknown'),
            'Duration': audio.info.length
        }
        return metadata
    except ID3NoHeaderError:
        print("No ID3 header found. The file may not be an MP3 with ID3 tags.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
file_path = 'music.mp3'
metadata = read_music_metadata(file_path)
if metadata:
    for key, value in metadata.items():
        print(f"{key}: {value}")
