import os
import time
import pyautogui

# Open and read the file
with open('fpga', 'r') as file:
    lines = file.readlines()

# Parse the file to extract (price, link) pairs
data = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('$'):
        price = line
        link = lines[i + 1].strip()
        data.append((price, link))
        i += 2  # Move to the next pair
    else:
        i += 1

# Iterate through the list and perform the required operations
for index, (price, link) in enumerate(data):
    # Open the link in Google Chrome
    os.system(f'google-chrome "{link}"')

    # Wait for the page to load
    time.sleep(5)  # Adjust the sleep time if needed

    # Save the page with the specified naming convention
    save_as_name = f'cpp_{price[1:]}_{index + 1}.html'
    
    # Use pyautogui to simulate the keystrokes for saving the page
    pyautogui.hotkey('ctrl', 's')
    time.sleep(1)  # Adjust the sleep time if needed
    pyautogui.typewrite(save_as_name)
    time.sleep(1)  # Adjust the sleep time if needed
    pyautogui.press('enter')

    # Wait for the save operation to complete
    time.sleep(3)  # Adjust the sleep time if needed
