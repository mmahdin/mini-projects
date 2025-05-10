import requests
from bs4 import BeautifulSoup
import os
from weasyprint import HTML, CSS

# Step 1: Fetch the HTML page
url = 'https://qul.tarteel.ai/resources/musbat-layout/14'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Extract the desired <div>
target_div = soup.find(
    'div', {'data-controller': 'mushaf-page tajweed-highlight'})
if not target_div:
    raise Exception("Target div not found")

html_content = str(target_div)

# Step 3: Find all linked CSS files
css_links = []
for link in soup.find_all('link', rel='stylesheet'):
    href = link.get('href')
    if href and href.startswith(('http', '//')):
        css_links.append(href if href.startswith('http') else f'https:{href}')
    elif href:  # Handle relative paths
        css_links.append(requests.compat.urljoin(url, href))

# Step 4: Download CSS files
css_dir = 'css_files'
os.makedirs(css_dir, exist_ok=True)
local_css_paths = []

for css_url in css_links:
    try:
        css_response = requests.get(css_url)
        css_response.raise_for_status()
        filename = os.path.join(
            css_dir, os.path.basename(css_url.split('?')[0]))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(css_response.text)
        local_css_paths.append(filename)
    except Exception as e:
        print(f"Failed to download {css_url}: {e}")

# Step 5: Wrap HTML with a minimal <html><head> to include styles
combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {"".join([f'<link rel="stylesheet" href="{path}">' for path in local_css_paths])}
</head>
<body>
{html_content}
</body>
</html>
"""

# Step 6: Convert to PDF
css_objects = [CSS(filename=path) for path in local_css_paths]
HTML(string=combined_html, base_url=url).write_pdf(
    'output.pdf', stylesheets=css_objects)

print("✅ PDF successfully created as output.pdf")
