#!/bin/bash
# Using xdotool and wmctrl to simulate mouse and keyboard actions

# Find the window ID of the application using its name
APP_NAME="GPT4All v2.7.5"
window_id=$(xdotool search --name "$APP_NAME")

PNG_NAME="Docker Desktop"
png_id=$(xdotool search --name "$PNG_NAME")
echo "PNG ID: $png_id"

# Check if the window ID was found
if [ -n "$window_id" ]; then
    # Simulate clicks at specified positions
    # Reduce the brightness of the screen

    xdotool windowactivate "$window_id"
    xdotool mousemove  1052 111 click 1
    xdotool mousemove  940 166 click 1

    xdotool windowactivate "$png_id"
    sleep 0.4
    xdotool windowactivate "$window_id"

    xdotool mousemove  295 214 click 1
    xdotool mousemove  295 214 click 1

    xdotool windowactivate "$png_id"
    sleep 0.2
    xdotool windowactivate "$window_id"
    # Paste the copied message and press Enter key
    xdotool mousemove 586 1017 click 1
    xdotool mousemove  549 1017 click 3

    xdotool windowactivate "$png_id"
    sleep 0.2
    xdotool windowactivate "$window_id"

    xdotool mousemove 586 1017 click 1
    xdotool mousemove 586 1017 click 1
    xdotool key Return

    xdotool windowminimize "$window_id"
    

else
    echo "Error: Window not found."
fi
