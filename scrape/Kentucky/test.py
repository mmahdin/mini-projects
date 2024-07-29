import requests
from bs4 import BeautifulSoup
import re

# Define proxy settings
proxies = {
    'http': 'socks5://127.0.0.1:2080',
    'https': 'socks5://127.0.0.1:2080'
}

# Define URL and headers for the request
url = 'https://kdla.ky.gov/Library-Support/Pages/Public-Library-Directory.aspx'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

# Sending HTTP request to the URL
response = requests.get(url, headers=headers, proxies=proxies)
print(response.status_code)

if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all divs with class 'media library'
    library_divs = soup.find_all('div', {'class': 'media library'})

    # Open the file in write mode
    with open("Libraries.xlsx", 'w') as file:
        # Loop through each library div
        for div in library_divs:
            media_body_div = div.find('div', {'class': 'media-body'})

            # Get library name
            library_name = media_body_div.find('h3').get_text()

            # Get and format library address
            address_tag = media_body_div.find('address')
            if address_tag:
                address_text = address_tag.get_text(separator=", ").strip()
                address_text = re.sub(
                    r"(\w{2,3}) (\d{5}-\d{4})", r"\1, \2", address_text)
            else:
                address_text = "Address not found"

            # Get additional information
            additional_info_div = media_body_div.find(
                'div', {'class': 'flex-mini-parent'})
            try:
                additional_info = additional_info_div.find_all(
                    'div', {'class': 'flex-mini-child'})[1].get_text()
            except (AttributeError, IndexError):
                additional_info = "None"

            # Combine information into a single line
            combined_info = f"{library_name}, {address_text}, {additional_info}"
            file.write(combined_info + '\n')
else:
    print("Failed to retrieve the webpage.")
