import PyPDF2


def extract_pages(input_pdf_path, output_pdf_path, pages_to_extract):
    # Open the original PDF file
    with open(input_pdf_path, 'rb') as input_pdf:
        reader = PyPDF2.PdfReader(input_pdf)
        writer = PyPDF2.PdfWriter()

        # Add the specified pages to the writer
        for page_num in pages_to_extract:
            # PyPDF2 uses zero-based indexing, so subtract 1 from the page number
            page = reader.pages[page_num - 1]
            writer.add_page(page)

        # Write the selected pages to a new PDF
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)


# Example usage
input_pdf_path = 'book.pdf'  # Replace with your input PDF path
# Replace with your desired output PDF path
output_pdf_path = 'madar.pdf'
# Pages to extract (1-based index)
pages_to_extract = [i for i in range(67, 75)]

extract_pages(input_pdf_path, output_pdf_path, pages_to_extract)
