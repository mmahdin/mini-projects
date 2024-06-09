import numpy as np
import cv2
import matplotlib.pyplot as plt

def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return image

def save_image(image_array, output_path):
    cv2.imwrite(output_path, image_array)

def pad_image(image, pad_width, pad_height):
    return np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='constant', constant_values=0)

def correlate(image, kernel):
    k_height, k_width = kernel.shape
    i_height, i_width = image.shape
    
    pad_height = k_height // 2
    pad_width = k_width // 2
    
    padded_image = pad_image(image, pad_width, pad_height)
    result = np.zeros_like(image)
    
    for i in range(i_height):
        for j in range(i_width):
            region = padded_image[i:i+k_height, j:j+k_width]
            result[i, j] = np.sum(region * kernel)
    
    return result

def create_impulse_image(size, impulse_position):
    image = np.zeros(size, dtype=np.float32)
    image[impulse_position] = 1.0
    return image



# -------------------------------------------------------
image_path = 'sharp.png'
image = load_image(image_path)
kernel = np.array([
        [ 0, -1,  0],
        [-1,  5, -1],
        [ 0, -1,  0]
])
# kernel = np.array([
#     [-1/9, -1/9, -1/9],
#     [-1/9, 2-1/9, -1/9],
#     [-1/9, -1/9, -1/9]
# ])
result = correlate(image, kernel)
result = np.clip(result, 0, 255).astype(np.uint8)
# cv2.imshow('org', image)
# cv2.imshow('corr', result)


# -------------------------------------------------------
image_size = (9, 9)
impulse_position = (4, 4)
impulse_image = create_impulse_image(image_size, impulse_position)

# Define the arbitrary filter F
# filter_kernel = np.array([
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ], dtype=np.float32)

filter_kernel = np.array([
    [9, 8, 3],
    [6, 5, 6],
    [3, 8, 9]
], dtype=np.float32)
# Perform correlation
result = correlate(impulse_image, filter_kernel)

# Display the impulse image and the result
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title('Impulse Image (I)')
plt.imshow(impulse_image, cmap='gray')
plt.colorbar()

plt.subplot(1, 2, 2)
plt.title('Resulting Image (G)')
plt.imshow(result, cmap='gray')
plt.colorbar()

# plt.show()


# -------------------------------------------------------
image_path = 'smoth.png'
image = load_image(image_path)
kernel = np.array([
        [0,   0, 0],
        [0, 255, 0],
        [0,   0, 0]
])

result = correlate(image, kernel)
result = np.clip(result, 0, 255).astype(np.uint8)
# cv2.imshow('org', image)
# cv2.imshow('corr', result)

# -------------------------------------------------------
image_path = 'sharp.png'
image = load_image(image_path)
kernel = (1/16) * np.array([
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]
])

result = correlate(image, kernel)
result = np.clip(result, 0, 255).astype(np.uint8)
cv2.imshow('org', image)
cv2.imshow('corr', result)





cv2.waitKey(0)
cv2.destroyAllWindows()

