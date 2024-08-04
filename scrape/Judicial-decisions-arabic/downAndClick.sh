#!/bin/bash

# Activate Chrome window (assumes Chrome is open)
xdotool windowactivate $(xdotool search --name "البوابة القضائية العلمية - Google Chrome")


sleep 0.1
xdotool mousemove 525 394 click 1
sleep 0.1

for i in {1..50}; do
    xdotool click 5
    sleep 0.0001
done

