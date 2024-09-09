import PyPDF2
from pdf2image import convert_from_path
import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract


def extract_page(pdf_path, page):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        first_page = reader.getPage(page)
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
    hs = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        line_positions.append(x)
        hs.append([h, y])
    h_max = sorted(hs, key=lambda x: x[0], reverse=True)[0]
    # Sort the lines by width in descending order
    line_positions = sorted(line_positions)

    line_positions = [0] + line_positions + [image.shape[1]-150]

    cropped_images = []
    for i in range(len(line_positions) - 1):
        x_start = line_positions[i]
        x_end = line_positions[i + 1]
        cropped_img = image[:h_max[0] + h_max[1], x_start:x_end]
        cropped_images.append(cropped_img)
    if show:
        # plt.imshow(cv2.cvtColor(cropped_images[0], cv2.COLOR_BGR2RGB))
        cv2.imwrite('cropped.png', cropped_images[0])
        # plt.show()

    return cropped_images


def rows(gray):
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('s', thresh)
    # cv2.waitKey(0)
    height = gray.shape[0]
    min_white_space_height = 8
    start_y = 0
    segments = []
    avg1 = 0
    for y in range(height):
        # Check the number of white pixels in the current row
        white_pixels = cv2.countNonZero(thresh[y:y+1, :])
        if white_pixels < 5:
            # If white pixels are detected, it means the start of a text block
            if start_y == 0:
                start_y = y
        elif white_pixels > 5 and start_y != 0:
            # If no white pixels and start_y is set, it means end of a text block
            end_y = y
            # Check if the white space is enough to consider it as separation
            if end_y - start_y > min_white_space_height:
                # Crop the text block
                avg2 = int((start_y + end_y) / 2)
                segment = gray[avg1:avg2, :]
                avg1 = avg2
                segments.append(segment)
            start_y = 0
    segments.append(gray[avg2:y, :])

    # Save each segment as an individual image
    for i, segment in enumerate(segments):
        cv2.imwrite(f'./cropped/segment_{i}.png', segment)

    return segments


def one_page_extract(page):
    # Example usage
    pdf_path = 'pdf.pdf'  # Replace with your PDF path
    first_page_path = extract_page(pdf_path, page)
    image_path = pdf_to_image(first_page_path, 'first_page.png')
    h_lines = detect_lines(image_path, 2)
    v_lines = detect_lines(image_path, 3)

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.add(gray, cv2.bitwise_not(h_lines))
    gray = cv2.add(gray, cv2.bitwise_not(v_lines))

    try:
        lower_part = split_horizontaly(gray, h_lines)
    except:
        lower_part = gray

    cv2.imwrite('finalimg.png', lower_part)

    lists_image = split_verticaly(lower_part, v_lines, show=1)
    template_image = cv2.imread('template.png')
    template_image_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

    col_list = []
    for i in [0, 5, 6, 7, 11]:
        segments = rows(lists_image[i])
        custom_config = r'--psm 6'
        seg_list = []
        for seg in segments[1:]:
            text = pytesseract.image_to_string(seg, config=custom_config)
            text = text.replace('\n', '').replace(',', '/')
            try:
                result = cv2.matchTemplate(
                    seg, template_image_gray, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                threshold = 0.8
                if max_val >= threshold:
                    text = '-'
            except:
                continue
            if text == '':
                continue
            if not text.isupper():
                if not 'Continued' in text:
                    seg_list.append(text)

        print(len(seg_list), ' for ', i)
        col_list.append(seg_list)
    return col_list


with open('res.csv', 'w') as file:
    for p in range(10):
        print(f'-----------page{p}')
        col_list = one_page_extract(p)
        for i in range(len(col_list[0])):
            for j in range(len(col_list)):
                file.write(col_list[j][i] + ',')
            file.write('\n')
