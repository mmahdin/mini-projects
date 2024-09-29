from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import cv2
import numpy as np
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from bs4 import BeautifulSoup


class MultiFileCreationHandler(FileSystemEventHandler):
    def __init__(self, file_callbacks):
        # A dictionary that maps file names to their respective callback functions
        self.file_callbacks = file_callbacks

    def on_created(self, event):
        # Loop through all the files and check if the event matches any
        for file_name, callback in self.file_callbacks.items():
            if event.src_path.endswith(file_name):
                print(f"'{file_name}' file detected!")
                callback()  # Call the corresponding function


def file_detected_action():
    driver.quit()


def imageProcessing(template_image_path='/home/mahdi/Documents/mini-projects/scrape/playmusic/sub.png'):
    # Load the main image and the template image
    main_image_path = '/home/mahdi/Documents/mini-projects/scrape/playmusic/screenshot.png'
    main_image = cv2.imread(main_image_path)
    template_image = cv2.imread(template_image_path)

    # Convert images to grayscale
    main_image_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    template_image_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

    # Get the dimensions of the template image
    w, h = template_image_gray.shape[::-1]

    # Perform template matching
    result = cv2.matchTemplate(
        main_image_gray, template_image_gray, cv2.TM_CCOEFF_NORMED)
    # Set a threshold for detecting the match
    threshold = 0.8
    loc = np.where(result >= threshold)

    main_image_shape = main_image.shape
    print(f"Shape of the main image: {main_image_shape}")
    print(f"Shape of the sub image: {template_image.shape}")

    # Crop the detected area (assuming the first match is the one you want)
    if loc[0].size > 0:
        top_left = (loc[1][0], loc[0][0])
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cropped_image = main_image[top_left[1]                                   :bottom_right[1], top_left[0]:bottom_right[0]]
        print(f"Shape of the cropped image: {cropped_image.shape}")

        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        print(f"Center of the detected template: ({
              center_x}, {center_y})")

        # Save the cropped image
        cropped_image_path = '/home/mahdi/Documents/mini-projects/scrape/playmusic/cropped_image.jpg'
        cv2.imwrite(cropped_image_path, cropped_image)

        return [center_x, center_y]

        # Display the cropped image
        # cv2.imshow('Cropped Image', cropped_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        print("Template not found in the main image.")


def read_and_remove_first_line(file_path='/home/mahdi/Documents/mini-projects/scrape/playmusic/musicList.txt'):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if lines:
        first_line = lines[0].strip()
    else:
        first_line = None

    with open(file_path, 'w') as file:
        file.writelines(lines[1:])

    return first_line


def file_close_detected_action():
    driver.quit()


def file_download_detected_action():
    global url
    with open('/home/mahdi/Documents/mini-projects/scrape/playmusic/liked_music', 'a') as file:
        file.write(url + '\n')


def play():
    global url
    url = read_and_remove_first_line()
    driver.get(url)
    time.sleep(2)

    try:
        pakh_div = driver.find_element(By.CLASS_NAME, 'pakh')
        driver.execute_script("arguments[0].scrollIntoView();", pakh_div)
    except NoSuchElementException:
        print("\a")
        return

    driver.save_screenshot(
        "/home/mahdi/Documents/mini-projects/scrape/playmusic/screenshot.png")

    x, y = imageProcessing(
        template_image_path='/home/mahdi/Documents/mini-projects/scrape/playmusic/sub.png')

    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()

    #####################################################################################
    path = '/home/mahdi/play_music/'
    file_callbacks = {
        'close': file_close_detected_action,
        'like': file_download_detected_action
    }

    # Create an event handler for detecting multiple files
    event_handler = MultiFileCreationHandler(file_callbacks)

    observer = Observer()
    # Monitor only the specified directory
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        # Keep the observer running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()  # Gracefully stop the observer
    observer.join()


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1850,1050")

chrome_driver_path = '/home/mahdi/app/chromedriver-linux64/chromedriver'

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = ''
play()
