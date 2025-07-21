from playwright.sync_api import sync_playwright
import cv2
import numpy as np
from PIL import Image
import time


mask_paths = {
    'enable_loc': 'masks/enable_loc.png',
    'allow_loc': 'masks/allow_loc.png',
    'snap': 'masks/snap.png',
    'close_rating': 'masks/close_rating.png',
    'find_origin': 'masks/find_origin.png',
    'origin_confirm': 'masks/origin_confirm.png',
    'chosen_loc': 'masks/chosen_loc.png',
    'where_you_go': 'masks/where_you_go.png',
    'destination_confirm': 'masks/destination_confirm.png',
    'getting_snap': 'masks/getting_snap.png',
    'for_others': 'masks/for_others.png',
    'others': 'masks/others.png',
    'enter_others_inf': 'masks/enter_others_inf.png',
    'others_name': 'masks/others_name.png',
    'others_number': 'masks/others_number.png'
}

storage_file = 'loggin/auth.json'

url = 'https://app.snapp.taxi/?utm_source=website&utm_medium=webapp-button&utm_campaign=body'

delay = 3


def find_mask_in_screenshot(screen_path, mask_path, threshold=0.85):
    # Load images
    screen = cv2.imread(screen_path)
    mask = cv2.imread(mask_path)

    # Template matching
    res = cv2.matchTemplate(screen, mask, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        h, w = mask.shape[:2]
        return max_loc[0] + w // 2, max_loc[1] + h // 2  # center point
    return None


def capture_screenshot(page, path="screenshot.png"):
    page.screenshot(path=path, full_page=True)


def click_mask(page, mask_path):
    screenshot_path = "screenshot.png"
    capture_screenshot(page, screenshot_path)
    coords = find_mask_in_screenshot(screenshot_path, mask_path)
    if coords:
        page.mouse.click(coords[0], coords[1])
        print(f"Clicked on mask at {coords}")
        return True
    else:
        print("Mask not found.")
        return False


def run_with_login(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            storage_state=storage_file,
            geolocation={"latitude": 35.9680991, "longitude": 50.7372719},
            permissions=["geolocation"],
            locale="en-US"
        )

        page = context.new_page()
        page.goto(url)
        time.sleep(5)

        # clicking on snap
        mask = mask_paths['snap']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['close_rating']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['find_origin']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        page.keyboard.type(data['origin'])
        time.sleep(delay)

        mask = mask_paths['chosen_loc']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['origin_confirm']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['where_you_go']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        page.keyboard.type(data['destination'])
        time.sleep(delay)

        mask = mask_paths['chosen_loc']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['destination_confirm']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['for_others']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['others']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['enter_others_inf']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        mask = mask_paths['others_name']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        page.keyboard.type(data['name'])
        time.sleep(delay)

        mask = mask_paths['others_number']
        found = click_mask(page, mask)
        if not found:
            print(f"Failed to find {mask}")
        time.sleep(delay)

        page.keyboard.type(data['number'])
        time.sleep(delay)

        time.sleep(20)


data = {
    'origin': '35.9680991, 50.7372719',
    'destination': '35.9730182, 50.7326614',
    'name': 'محمدجعفری',
    'number': '09188861828'
}

run_with_login(data)
