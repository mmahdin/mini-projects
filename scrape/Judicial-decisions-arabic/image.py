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
        cropped_image = main_image[top_left[1]                                   :bottom_right[1], top_left[0]:bottom_right[0]]
        print(f"Shape of the cropped image: {cropped_image.shape}")

        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        print(f"Center of the detected template: ({
              center_x}, {center_y})")

        # Save the cropped image
        cropped_image_path = 'cropped_image.jpg'
        cv2.imwrite(cropped_image_path, cropped_image)

        # Display the cropped image
        cv2.imshow('Cropped Image', cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return [center_x, center_y]
    else:
        print("Template not found in the main image.")


imageProcessing()
