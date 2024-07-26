import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image_path = "img6.png"
image = cv2.imread(image_path)
# image = cv2.resize(image, (500, 800), interpolation=cv2.INTER_AREA)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_non_squares(image, num=1):
    blurred_img = cv2.GaussianBlur(image, (5, 5), 0)
    # Convert image to grayscale
    gray = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2GRAY)
    # Apply threshold to get binary image

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    kernel = np.ones((65, 65), np.uint8)
    opened_image = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('thrsh', opened_image)
    # cv2.waitKey(0)

    # Find contours
    contours, _ = cv2.findContours(
        opened_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    largest_contour = contours[1]

    blank_image = np.zeros_like(gray)
    # Drawing with green color and thickness 3
    cv2.drawContours(
        blank_image, [largest_contour], -1, (255), thickness=cv2.FILLED)
    try:
        cv2.drawContours(
            blank_image, [contours[2]], -1, (255), thickness=cv2.FILLED)
    except:
        pass

    cv2.imshow('thrsh', opened_image)
    cv2.waitKey(0)

    mask = np.zeros_like(gray)

    for contour in contours:
        # Approximate the contour
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            cv2.drawContours(mask, [contour], -1, (255), thickness=cv2.FILLED)

    # Create the final image where only squares are retained
    result = cv2.bitwise_and(image, image, mask=blank_image)
    return result


# squares_image = remove_non_squares(image.copy())

# # Convert the image to RGB for display
# squares_image_rgb = cv2.cvtColor(squares_image, cv2.COLOR_BGR2RGB)


# plt.figure(figsize=(15, 8))
# plt.imshow(squares_image_rgb)
# plt.axis('off')
# plt.show()
