import PyPDF2
from pdf2image import convert_from_path
import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract


def extract_first_page(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        first_page = reader.getPage(0)
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(first_page)

        with open('first_page.pdf', 'wb') as output_file:
            pdf_writer.write(output_file)

    return 'first_page.pdf'


def pdf_to_image(pdf_path, output_image_path):
    images = convert_from_path(pdf_path)
    first_image = images[0]
    first_image.save(output_image_path, 'PNG')
    return output_image_path


def detect_lines(image_path, typ=1):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine horizontal and vertical lines
    if typ == 1:
        lines = cv2.add(horizontal_lines, vertical_lines)
    elif typ == 2:
        lines = horizontal_lines
    else:
        lines = vertical_lines

    inverted_image = cv2.bitwise_not(lines)

    kernel = np.ones((3, 3), np.uint8)
    thick_lines = cv2.erode(inverted_image, kernel, iterations=2)

    cv2.imwrite('detected_lines.png', thick_lines)

    return thick_lines


def split_horizontaly(image, lines, show=0):
    lines = cv2.bitwise_not(lines)

    contours, _ = cv2.findContours(
        lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    line_info = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        line_info.append((w, y, x))

    # Sort the lines by width in descending order
    line_info = sorted(line_info, key=lambda x: x[0], reverse=True)
    line_info = sorted(line_info, key=lambda x: x[2], reverse=False)

    # Get the position of the second largest horizontal line
    if len(line_info) >= 2:
        _, y, _ = line_info[0]  # The second largest line
    else:
        raise ValueError(
            "There are not enough horizontal lines to find the second largest one.")

    upper_part = image[:y, :]
    lower_part = image[y:, :]

    if show:
        plt.figure(figsize=(10, 10))
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(upper_part, cv2.COLOR_BGR2RGB))
        plt.title('Upper Part')

        plt.subplot(1, 2, 2)
        plt.imshow(cv2.cvtColor(lower_part, cv2.COLOR_BGR2RGB))
        plt.title('Lower Part')
        plt.show()

    return lower_part


def split_verticaly(image, lines, show=0):
    lines = cv2.bitwise_not(lines)

    contours, _ = cv2.findContours(
        lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    line_positions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        line_positions.append(x)

    # Sort the lines by width in descending order
    line_positions = sorted(line_positions)

    print(line_positions)

    line_positions = [0] + line_positions + [image.shape[1]-150]

    cropped_images = []
    for i in range(len(line_positions) - 1):
        x_start = line_positions[i]
        x_end = line_positions[i + 1]
        cropped_img = image[:, x_start:x_end]
        cropped_images.append(cropped_img)

    if show:
        plt.imshow(cv2.cvtColor(cropped_images[-1], cv2.COLOR_BGR2RGB))
        cv2.imwrite('cropped.png', cropped_images[-1])
        plt.show()

    return cropped_images


# Example usage
pdf_path = 'pdf.pdf'  # Replace with your PDF path
first_page_path = extract_first_page(pdf_path)
image_path = pdf_to_image(first_page_path, 'first_page.png')
h_lines = detect_lines(image_path, 2)

image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

lower_part = split_horizontaly(gray, h_lines)

v_lines = detect_lines(image_path, 3)

lists_image = split_verticaly(lower_part, v_lines, show=1)

# try with tesseract
custom_config = r'--psm 6'
lists_text = []
for i in lists_image:
    lists_text.append(pytesseract.image_to_string(
        i, config=custom_config))

print(lists_text[-1])
# with open('res.csv', 'w') as file:
#     for i in range(len(lists_image[0])):
#         for j in lists_text:
#             file.write(j[i].replase(',', '/')+',')
#         file.write('\n')
