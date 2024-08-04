#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the filename for the screenshot
FILENAME="screenshot.png"

# Take a screenshot and save it in the script's directory
import -window root "$SCRIPT_DIR/$FILENAME"

# Notify the user
echo "Screenshot saved as $SCRIPT_DIR/$FILENAME"
