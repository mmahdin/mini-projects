#!/bin/bash

# Directory containing .mp4 files
DIRECTORY="/home/mahdi/Documents/mini-projects/instagram-English-learning/words.2u"

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
  echo "Directory does not exist."
  exit 1
fi

# Find all .mp4 files in the directory
FILES=("$DIRECTORY"/*.mp4)

# Check if there are any .mp4 files
if [ ${#FILES[@]} -eq 0 ]; then
  echo "No .mp4 files found in the directory."
  exit 1
fi

# Select a random .mp4 file
RANDOM_FILE=${FILES[RANDOM % ${#FILES[@]}]}

# Play the selected file using VLC
vlc "$RANDOM_FILE"
