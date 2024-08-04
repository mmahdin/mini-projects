#!/bin/bash

# Check if the correct number of arguments are passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <x> <y>"
    exit 1
fi

# Get the x and y coordinates from the arguments
X=$1
Y=$2

# Move the mouse to the specified position and click
xdotool mousemove $X $Y click 1