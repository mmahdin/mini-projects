#!/bin/bash

# Activate Chrome window (assumes Chrome is open)
xdotool windowactivate $(xdotool search --name "البوابة القضائية العلمية - Google Chrome")


for i in {1..50}; do
    xdotool click 4
    sleep 0.0001
done