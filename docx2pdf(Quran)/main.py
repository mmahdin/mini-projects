from docx import Document
from weasyprint import HTML
import re

# Remove control characters and fix curly brace direction in RTL text


def clean_text(text):
    # Remove invisible Unicode control characters
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', text)

    # Force correct direction for LTR characters in RTL context
    text = text.replace('{', '<span dir="ltr">{</span>')
    text = text.replace('}', '<span dir="ltr">}</span>')

    return text.strip()

# Convert DOCX content to HTML with proper styling


def docx_to_html(docx_path):
    doc = Document(docx_path)
    html = ['<html lang="ar" dir="rtl"><head><meta charset="UTF-8">']
    html.append("""
    <style>
        @font-face {
            font-family: 'Amiri';
            src: local('Amiri'), url('https://fonts.gstatic.com/s/amiri/v19/J7aRnpd8CGxBHqUp.woff2') format('woff2');
        }
        body {
            font-family: 'Amiri', 'Scheherazade', 'Traditional Arabic', serif;
            direction: rtl;
            text-align: justify;
            margin: 2cm;
            font-size: 22px;
            line-height: 2.2;
        }
        p {
            margin-bottom: 1em;
        }
    </style></head><body>
    """)

    for para in doc.paragraphs:
        text = clean_text(para.text)
        if text:
            html.append(f'<p>{text}</p>')

    html.append('</body></html>')
    return '\n'.join(html)

# Convert the styled HTML to PDF


def convert_docx_to_pdf(docx_file, output_pdf):
    html_content = docx_to_html(docx_file)
    HTML(string=html_content).write_pdf(output_pdf)
    print(f"✅ Successfully converted '{docx_file}' to '{output_pdf}'")


# Example usage
if __name__ == "__main__":
    name = '595'
    input_path = f"{name}.docx"  # Change this to your DOCX file
    output_path = f"{name}.pdf"
    convert_docx_to_pdf(input_path, output_path)
