import fitz  # PyMuPDF


def extract_words_from_pdf(pdf_path):
    words = []
    # Open the PDF file
    with fitz.open(pdf_path) as pdf:
        # Loop through each page in the PDF
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text = page.get_text("text")
            # Split the text by lines
            lines = text.splitlines()

            # Loop through lines to find words based on pattern
            for line in lines:
                # Look for lines with the pattern "word (part_of_speech): meaning"
                if ("(" in line or ')' in line) and ":" in line:
                    # Extract the word before the "("
                    word = line.split("(")[0].strip()
                    word = word.split(")")[0].strip() + '\n'
                    words.append(word)

    return words


# Example usage
with open('words', 'w') as file:
    for i in range(1, 51):
        # Path to your PDF file
        pdf_path = f"/home/mahdi/Documents/konkur/English/{i}.pdf"
        extracted_words = extract_words_from_pdf(pdf_path)
        file.writelines(extracted_words)
