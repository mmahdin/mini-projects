import fitz  # PyMuPDF


def extract_pdf_to_text(pdf_path, text_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    with open(text_path, 'w') as text_file:
        for page_num in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_num)
            # Extract text from the page
            text = page.get_text("text")
            # Write the text to the text file
            text_file.write(text)
            text_file.write('\n')  # Ensure a new line between pages
            break


# Usage
pdf_path = 'pdf.pdf'
text_path = 'rowtxt'
extract_pdf_to_text(pdf_path, text_path)


with open(text_path, 'r') as file:
    lines = file.readlines()

lines = lines[33:]

with open('rowtxt2.csv', 'w') as file:
    for i in range(len(lines)):
        file.write(lines[i].replace('\n', '').replace(
            ',', '/').replace("'", "/") + ',')
        if i % 13 == 0:
            file.write('\n')
