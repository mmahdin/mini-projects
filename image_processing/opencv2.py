import cv2
import numpy as np
import matplotlib.pyplot as plt

def uniform_scaling(image, scale_factor):
    if scale_factor <= 0:
        raise ValueError("Scale factor must be greater than 0")

    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Compute the new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Perform the scaling
    scaled_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    return scaled_image


def shear_image(image, shear_factor_x=0.0, shear_factor_y=0.0):
    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Define the shear transformation matrix
    shear_matrix = np.array([
        [1, shear_factor_x, 0],
        [shear_factor_y, 1, 0]
    ], dtype=np.float32)

    # Compute the new dimensions to fit the entire sheared image
    new_width = int(width + abs(shear_factor_y) * height)
    new_height = int(height + abs(shear_factor_x) * width)

    # Apply the shear transformation
    sheared_image = cv2.warpAffine(image, shear_matrix, (new_width, new_height))

    return sheared_image


# -------------------------------------------------------
image = cv2.imread("img.png")
scaled_image = uniform_scaling(image, 0.5)
cv2.imshow('Original Image', image)
cv2.imshow('Scaled Image', scaled_image)

# -------------------------------------------------------
image = cv2.imread("img.png")
shear_factor_x = 0.3
shear_factor_y = 0.0
sheared_image = shear_image(image, shear_factor_x, shear_factor_y)
# cv2.imshow('Original Image', image)
# cv2.imshow('Sheared Image', sheared_image)

# -------------------------------------------------------



# cv2.imshow("example" , image)
cv2.waitKey(0)
cv2.destroyAllWindows()