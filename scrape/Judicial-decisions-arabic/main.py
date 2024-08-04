import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
import time
import cv2
import numpy as np


def imageProcessing():
    # Load the main image and the template image
    main_image_path = 'screenshot.png'
    template_image_path = 'sub.png'
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
        cropped_image = main_image[top_left[1]
            :bottom_right[1], top_left[0]:bottom_right[0]]
        print(f"Shape of the cropped image: {cropped_image.shape}")

        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        print(f"Center of the detected template: ({
              center_x}, {center_y})")

        # Save the cropped image
        cropped_image_path = 'cropped_image.jpg'
        cv2.imwrite(cropped_image_path, cropped_image)

        return [center_x, center_y]

        # Display the cropped image
        # cv2.imshow('Cropped Image', cropped_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        print("Template not found in the main image.")


def click_position(x, y):
    # Path to the bash script
    script_path = './click.sh'

    # Run the bash script with x and y as arguments
    result = subprocess.run([script_path, str(x), str(y)],
                            capture_output=True, text=True)

    # Print the output and errors (if any)
    print("Output:", result.stdout)
    print("Error:", result.stderr)


# Define proxy settings
options = webdriver.ChromeOptions()
options.add_argument("--start-fullscreen")

# Define URL and headers for the request
url = 'https://sjp.moj.gov.sa/Filter?SubjectValue=10'


chrome_driver_path = '/home/mahdi/app/chromedriver-linux64/chromedriver'
go2down = "./downAndClick.sh"
screenshot = './screen.sh'
up = './up.sh'

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

scr_flg = 0
gcnt = 1
links = []
base_addr = 'https://sjp.moj.gov.sa'
driver.get(url)
while gcnt != 55560:
    time.sleep(5)

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    div1 = soup.find_all('div', {'id': 'DivFilteredData'})[0]

    div2 = div1.find_all(
        'div', {'class': "degrees-article bt-padding hidden-sm hidden-xs", 'id': "th"})[0]

    tbody = div2.find_all('tbody')[0]

    trs = tbody.find_all('tr')

    for tr in trs:
        td = tr.find_all('td', {'class': "col-xs-8 pad-15 pointer"})[0]
        link = td.get('onclick').split("'")[1]
        links.append(base_addr + link)
        gcnt += 1

    print(links)

    result = subprocess.run([go2down])
    result = subprocess.run([screenshot])
    x, y = imageProcessing()
    click_position(x, y)
    time.sleep(5)
    result = subprocess.run([up])

driver.get(links[0])
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
section = soup.find_all('section', {'class': 'accordion tp-margin'})[0]
div = section.find_all('div', {'class': "panel-body main2-color"})[0]
h5 = div.find_all('h5')[0]


# Close the browser
driver.quit()
