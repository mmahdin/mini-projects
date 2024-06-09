import cv2
import numpy as np
import matplotlib.pyplot as plt

def gamma_correction(image, gamma, c=1):
    # Ensure the image is in the float32 format and normalize the pixel values to [0, 1]
    img_float = image.astype(np.float32) / 255.0
    
    # Apply the gamma correction formula
    corrected_img = c * np.power(img_float, gamma)
    
    # Clip the values to [0, 1] and convert back to the range [0, 255]
    corrected_img = np.clip(corrected_img, 0, 1)
    corrected_img = (corrected_img * 255).astype(np.uint8)
    
    return corrected_img


def negative_image(image):
    # Subtract each pixel value from 255
    negative = 255 - image
    return negative


def log_transform(image):
    # Convert the image to float32 to prevent overflow/underflow issues
    image_float = image.astype(np.float32)
    # Apply the log transformation
    c = 255 / np.log(1 + np.max(image_float))
    log_image = c * np.log(1 + image_float)
    # Clip values to ensure they are within [0, 255]
    log_image = np.clip(log_image, 0, 255)
    # Convert back to uint8
    log_image = log_image.astype(np.uint8)
    return log_image


def contrast_stretching(image, r1, s1, r2, s2):
    L = 256  # Assuming 8-bit grayscale image
    
    # Define the transformation function
    def transform_pixel(pixel):
        if pixel <= r1:
            return (s1 / r1) * pixel
        elif pixel <= r2:
            return ((s2 - s1) / (r2 - r1)) * (pixel - r1) + s1
        else:
            return ((L - 1 - s2) / (L - 1 - r2)) * (pixel - r2) + s2

    # Vectorize the transformation function
    vectorized_transform = np.vectorize(transform_pixel)
    
    # Apply the transformation
    stretched_image = vectorized_transform(image)
    
    # Clip values to ensure they are within [0, 255] and convert back to uint8
    stretched_image = np.clip(stretched_image, 0, 255).astype(np.uint8)
    
    return stretched_image


def plot_histogram(image):
    # Calculate the histogram for the image
    histogram = cv2.calcHist([image], [0], None, [256], [0, 256])
    
    # Plot the histogram using Matplotlib
    plt.figure()
    plt.title("Grayscale Histogram")
    plt.xlabel("Intensity Value")
    plt.ylabel("Frequency")
    plt.plot(histogram)
    plt.xlim([0, 256])  # Set the x-axis range to [0, 256]
    plt.show()


def plot_cumulative_histogram(image):
    # Calculate the histogram for the image
    histogram = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    
    # Calculate the cumulative histogram
    cumulative_histogram = np.cumsum(histogram)
    
    # Normalize the cumulative histogram
    cumulative_histogram = cumulative_histogram / cumulative_histogram.max() * 255
    
    # Plot the cumulative histogram using Matplotlib
    plt.figure()
    plt.title("Cumulative Grayscale Histogram")
    plt.xlabel("Intensity Value")
    plt.ylabel("Cumulative Frequency")
    plt.plot(cumulative_histogram, color='r')
    plt.xlim([0, 256])  # Set the x-axis range to [0, 256]
    plt.show()


def histogram_equalization(image):
    # Apply histogram equalization using OpenCV
    equalized_image = cv2.equalizeHist(image)
    return equalized_image

def plot_histograms(original_image, equalized_image):
    # Calculate histograms
    original_hist = cv2.calcHist([original_image], [0], None, [256], [0, 256]).flatten()
    equalized_hist = cv2.calcHist([equalized_image], [0], None, [256], [0, 256]).flatten()

    original_cumulative_histogram = np.cumsum(original_hist)
    original_cumulative_histogram = original_cumulative_histogram / original_cumulative_histogram.max() * 255

    equalized_cumulative_histogram = np.cumsum(equalized_hist)
    equalized_cumulative_histogram = equalized_cumulative_histogram / equalized_cumulative_histogram.max() * 255

    # Plot histograms
    plt.figure(figsize=(12, 9))

    plt.subplot(3, 2, 1)
    plt.title("Original Image")
    plt.imshow(original_image, cmap='gray')
    plt.axis('off')

    plt.subplot(3, 2, 2)
    plt.title("Equalized Image")
    plt.imshow(equalized_image, cmap='gray')
    plt.axis('off')

    plt.subplot(3, 2, 3)
    plt.title("Original Histogram")
    plt.xlabel("Intensity Value")
    plt.ylabel("Frequency")
    plt.plot(original_hist)
    plt.xlim([0, 256])

    plt.subplot(3, 2, 4)
    plt.title("Equalized Histogram")
    plt.xlabel("Intensity Value")
    plt.ylabel("Frequency")
    plt.plot(equalized_hist)
    plt.xlim([0, 256])

    plt.subplot(3, 2, 5)
    plt.title("Cumulative Grayscale Histogram of Original")
    plt.xlabel("Intensity Value")
    plt.ylabel("Cumulative Frequency")
    plt.plot(original_cumulative_histogram, color='r')

    plt.subplot(3, 2, 6)
    plt.title("Cumulative Grayscale Histogram of Equalized")
    plt.xlabel("Intensity Value")
    plt.ylabel("Cumulative Frequency")
    plt.plot(equalized_cumulative_histogram, color='r')

    plt.tight_layout()
    plt.show()


def plot_pyramid(image):
    smaller = cv2.pyrDown(image)
    larger = cv2.pyrUp(image)

    plt.figure(figsize=(12, 9))

    plt.subplot(2,2,1)
    plt.title("smaller")
    plt.imshow(smaller, cmap='gray')

    plt.subplot(2,2,2)
    plt.title("larger")
    plt.imshow(larger, cmap='gray')

    smaller = cv2.pyrDown(smaller)
    larger = cv2.pyrUp(larger)

    plt.subplot(2,2,3)
    plt.title("more smaller")
    plt.imshow(smaller, cmap='gray')

    plt.subplot(2,2,4)
    plt.title("more larger")
    plt.imshow(larger, cmap='gray')

    plt.show()


# -------------------------------------------------------
image = cv2.imread('img.png')
gamma = [3,4,5]  # Example gamma value
for g in gamma:
    corrected_image = gamma_correction(image, g)
    # Save or display the corrected image
    cv2.imwrite(f'gamma{g}.png', corrected_image)

# -------------------------------------------------------
image = cv2.imread('negetiv.png')
negative_image_result = negative_image(image)

# -------------------------------------------------------
image = cv2.imread('log.png', cv2.IMREAD_GRAYSCALE)
corrected_image = gamma_correction(image, 0.2)
log_image = log_transform(image)

# -------------------------------------------------------
r1, s1 = 96, 64
r2, s2 = 110, 192
image = cv2.imread('stretching.png', cv2.IMREAD_GRAYSCALE)
stretched_image = contrast_stretching(image, r1, s1, r2, s2)

# -------------------------------------------------------
image = cv2.imread('stretching.png', cv2.IMREAD_GRAYSCALE)
# plot_histogram(image)

# -------------------------------------------------------
image = cv2.imread('stretching.png', cv2.IMREAD_GRAYSCALE)
# plot_cumulative_histogram(image)

# -------------------------------------------------------
image = cv2.imread('stretching.png', cv2.IMREAD_GRAYSCALE)
equalized_image = histogram_equalization(image)
# plot_histograms(image, equalized_image)

# -------------------------------------------------------
image = cv2.imread('stretching.png', cv2.IMREAD_GRAYSCALE)
plot_pyramid(image)

# cv2.imshow("log", stretched_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
