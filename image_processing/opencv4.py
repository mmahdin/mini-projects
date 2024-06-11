import cv2
import numpy as np
import matplotlib.pyplot as plt


def filter_2d_manual(image, kernel):
    image_height, image_width = image.shape
    kernel_height, kernel_width = kernel.shape
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2
    padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='constant', constant_values=0)
    filtered_image = np.zeros_like(image)

    for i in range(image_height):
        for j in range(image_width):
            region = padded_image[i:i + kernel_height, j:j + kernel_width]
            filtered_image[i, j] = np.sum(region * kernel)

    return filtered_image


def apply_sobel_operator(image):
    # Sobel kernels
    sobel_x = np.array([[-1, 0, 1], 
                        [-2, 0, 2], 
                        [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], 
                        [ 0,  0,  0], 
                        [ 1,  2,  1]])
    
    # Apply Sobel operator
    Gx = cv2.filter_2d_manual(image, sobel_x)
    Gy = cv2.filter_2d_manual(image, sobel_y)
    
    return Gx, Gy


def compute_gradient_magnitude_and_direction(Gx, Gy):
    # Calculate gradient magnitude
    gradient_magnitude = np.sqrt(Gx**2 + Gy**2)
    gradient_magnitude = convert_scale_abs(gradient_magnitude)
    
    # Calculate gradient direction
    gradient_direction = np.arctan2(Gy, Gx)
    
    return gradient_magnitude, gradient_direction


def convert_scale_abs(src):
    abs_src = np.abs(src)
    dst = np.uint8(np.clip(abs_src, 0, 255))
    return dst


def compute_image_gradient(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Image not found at the path: {image_path}")

    # Apply the Sobel operator to get the gradients in x and y directions
    Gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    Gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # Calculate the gradient magnitude
    gradient_magnitude = np.sqrt(Gx**2 + Gy**2)
    gradient_magnitude = cv2.convertScaleAbs(gradient_magnitude)  # Convert to 8-bit image

    # Calculate the gradient direction
    gradient_direction = np.arctan2(Gy, Gx)
    
    return gradient_magnitude, gradient_direction


def plot_intensity_and_derivative(image):
    if image is None:
        raise ValueError(f"Image not found at the path: {image_path}")
    
    # Select the middle row of the image
    middle_row = image[image.shape[0] // 2, :]
    
    # Plot the intensity as a function of position
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.title('Intensity as a function of position')
    plt.plot(middle_row)
    plt.xlabel('Position')
    plt.ylabel('Intensity')
    
    # Compute the derivative of the signal (intensity values)
    derivative = np.diff(middle_row)
    
    # Plot the derivative of the signal
    plt.subplot(1, 2, 2)
    plt.title('Derivative of the intensity')
    plt.plot(derivative)
    plt.xlabel('Position')
    plt.ylabel('d/dx of Intensity')
    
    plt.tight_layout()
    plt.show()


def gaussian_kernel(size, sigma=1.0):
    k = size // 2
    ax = np.linspace(-k, k, size)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
    return kernel / np.sum(kernel)


def apply_gaussian_smoothing(image, kernel_size=5, sigma=10.0):
    kernel = gaussian_kernel(kernel_size, sigma)
    smoothed_image = filter_2d_manual(image, kernel)
    return smoothed_image


def gaussian_derivative_kernels(size, sigma=0):
    k = size // 2
    ax = np.linspace(-k, k, size)
    xx, yy = np.meshgrid(ax, ax)
    
    gaussian = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
    gaussian /= np.sum(gaussian)
    
    # Derivative in x direction
    kernel_x = -xx * gaussian / np.square(sigma)
    # Derivative in y direction
    kernel_y = -yy * gaussian / np.square(sigma)
    
    return kernel_x, kernel_y


def apply_gaussian_derivatives(image, kernel_size=5, sigma=0):    
    # Generate Gaussian derivative kernels
    kernel_x, kernel_y = gaussian_derivative_kernels(kernel_size, sigma)
    
    # Convolve the image with the Gaussian derivative kernels
    gradient_x = filter_2d_manual(image, kernel_x)
    gradient_y = filter_2d_manual(image,  kernel_y)

    gradient_magnitude = compute_gradient_magnitude(gradient_x, gradient_y)
    
    plt.subplot(1, 2, 1)
    plt.title('Original Image')
    plt.imshow(image, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title('Gradient Magnitude')
    plt.imshow(gradient_magnitude, cmap='gray')
    plt.axis('off')

    plt.show()


def compute_gradient_magnitude(gradient_x, gradient_y):
    # Compute the gradient magnitude
    gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    return gradient_magnitude


def apply_gaussian_derivatives_opencv(image, kernel_size=5,  sigma=0):
    # Define different kernel sizes
    kernel_sizes = [(3, 3), (5, 5), (9, 9)]

    # Prepare to display results
    titles = ['Original Image', 'Gaussian X Derivative (3x3)', 'Gaussian Y Derivative (3x3)', 
            'Gradient Magnitude (3x3)', 'Gaussian X Derivative (5x5)', 'Gaussian Y Derivative (5x5)', 
            'Gradient Magnitude (5x5)', 'Gaussian X Derivative (9x9)', 'Gaussian Y Derivative (9x9)', 
            'Gradient Magnitude (9x9)']
    images = [image]

    # Apply Gaussian Blur with different kernel sizes and compute derivatives
    for ksize in kernel_sizes:
        blurred_image = cv2.GaussianBlur(image, ksize, 0)
        
        Gx = cv2.Sobel(blurred_image, cv2.CV_64F, 1, 0, ksize=3)
        Gy = cv2.Sobel(blurred_image, cv2.CV_64F, 0, 1, ksize=3)
        
        magnitude = cv2.magnitude(Gx, Gy)
        
        Gx = cv2.normalize(Gx, None, 0, 255, cv2.NORM_MINMAX)
        Gy = cv2.normalize(Gy, None, 0, 255, cv2.NORM_MINMAX)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        
        Gx = np.uint8(Gx)
        Gy = np.uint8(Gy)
        magnitude = np.uint8(magnitude)
        
        images.extend([Gx, Gy, magnitude])

    # Display the results
    plt.figure(figsize=(12, 12))
    for i in range(len(images)):
        plt.subplot(4, 3, i + 1)
        plt.imshow(images[i], cmap='gray')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])

    plt.tight_layout()
    plt.show()


# -------------------------------------------------------
image_path = './imgs/diff2.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
kernel_x = np.array([[-1, 0, 1],
                     [-2, 0, 2],
                     [-1, 0, 1]])
# kernel_x = np.array([[-1, 1]])
kernel_x = np.array([[0, 1],
                     [-1, 0]])
kernel_y = np.array([[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]])
# kernel_y = np.array([[1], [-1]])
kernel_y = np.array([[1, 0],
                     [0, -1]])
image_dx = filter_2d_manual(image, kernel_x)
image_dy = filter_2d_manual(image, kernel_y)

# cv2.imshow('Original Image', image)
# cv2.imshow('Differentiation in X axis', image_dx)
# cv2.imshow('Differentiation in Y axis', image_dy)


# -------------------------------------------------------
image_path = './imgs/diff1.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
gradient_magnitude, gradient_direction = compute_image_gradient(image_path)

# cv2.imshow("Gradient Magnitude", gradient_magnitude)
# cv2.imshow("Gradient Direction", gradient_direction / np.pi * 180)


# -------------------------------------------------------
image_path = './imgs/signal2.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
smoothed_image = apply_gaussian_smoothing(image)
# plot_intensity_and_derivative(image)
# plot_intensity_and_derivative(smoothed_image)
# cv2.imshow('original', image)
# cv2.imshow('smoothed image', smoothed_image)


# -------------------------------------------------------
image_path = './imgs/gauss_deriv.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# smoothed_image = apply_gaussian_smoothing(image)
# apply_gaussian_derivatives(smoothed_image)
apply_gaussian_derivatives_opencv(image,  kernel_size=5,  sigma=3) # first apply gaussian and then derivate.






cv2.waitKey(0)
cv2.destroyAllWindows()
