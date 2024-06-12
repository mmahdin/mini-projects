# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.ndimage import sobel

# # Create a 5x5 pixel image with different values
# image = np.array([
#     [0,0,0,0,0,0,0],
#     [0,0,0,0,0,0,0],
#     [0,0,1,1,1,0,0],
#     [0,0,1,1,1,0,0],
#     [0,0,1,1,1,0,0],
#     [0,0,0,0,0,0,0],
#     [0,0,0,0,0,0,0],
# ], dtype=np.float32)

# # Compute the gradient using Sobel filter
# sobel_x = sobel(image, axis=0)
# sobel_y = sobel(image, axis=1)

# # Calculate the magnitude and angle of the gradient
# magnitude = np.hypot(sobel_x, sobel_y)
# magnitude = magnitude / magnitude.max() * 255
# angle = np.arctan2(sobel_y, sobel_x)

# # Convert angle from radians to degrees
# angle = angle * 180. / np.pi
# angle_degrees = angle

# # Display the results
# print("Image:")
# print(image)

# print("\nGradient in x direction (Sobel x):")
# print(sobel_x)

# print("\nGradient in y direction (Sobel y):")
# print(sobel_y)

# print("\nGradient magnitude:")
# print(magnitude)

# print("\nGradient angle (in degrees):")
# print(angle_degrees)

# # Visualize the image and its gradient magnitude and angle
# plt.figure(figsize=(15, 5))

# plt.subplot(1, 3, 1)
# plt.title("Original Image")
# plt.imshow(image, cmap='gray')
# plt.colorbar()

# plt.subplot(1, 3, 2)
# plt.title("Gradient Magnitude")
# plt.imshow(magnitude, cmap='gray')
# plt.colorbar()

# plt.subplot(1, 3, 3)
# plt.title("Gradient Angle (Degrees)")
# plt.imshow(angle_degrees, cmap='hsv')  # Using hsv colormap to represent angles
# plt.colorbar()

# plt.show()

import cv2
import numpy as np

image_path = './imgs/canny.png'
gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Apply Gaussian blur to the grayscale image
blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 1.5)

# Apply Canny edge detection
edges = cv2.Canny(blurred_image, 100, 200)

# Save the resulting image
output_path = '/path/to/save/edges.jpg'  # Replace with your desired output path
cv2.imwrite(output_path, edges)

# Display the resulting image
cv2.imshow('Canny Edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()

