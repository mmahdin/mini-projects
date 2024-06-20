# Find the window ID of the application using its name
APP_NAME="GPT4All v2.7.5"
window_id=$(xdotool search --name "$APP_NAME")


# Check if the window ID was found
if [ -n "$window_id" ]; then
    xdotool windowactivate "$window_id"
    # copy
    xdotool mousemove 1719 125 click 1
    xdotool windowminimize "$window_id"
else
    echo "Error: Window not found."
fi