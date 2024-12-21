import requests
from bs4 import BeautifulSoup

# URL of the PhysioNet databases page
url = "https://physionet.org/about/database/"
base_url = 'https://physionet.org/'

# Fetch the page content
response = requests.get(url)
response.raise_for_status()  # Check for request errors

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

titles = []
links = []
if response.status_code == 200:
    print('ok')
    soup = BeautifulSoup(response.text, 'html.parser')
    uls = soup.find_all('ul')[5:8]
    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            # extract links
            links.append(base_url+li.find('a').get('href'))

            # extract titles
            # titles.append(li.text.replace('\n', '').replace(
            #     '   ', '').replace('   ', '').replace('   ', ''))

with open('links.txt', 'w') as f:
    for i in links:
        f.write(i + '\n')

# with open('titles.txt', 'w') as f:
#     for i in titles:
#         f.write(i + '\n')
