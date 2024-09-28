import requests
from bs4 import BeautifulSoup
import time

# URL of the website
url = 'https://music-doni.ir/'

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

output_file = 'musics.txt'
last_page_file = 'last_page.txt'


def save_last_page(page_number):
    with open(last_page_file, 'w') as f:
        f.write(str(page_number))


def load_last_page():
    try:
        with open(last_page_file, 'r') as f:
            return int(f.read())
    except FileNotFoundError:
        return 1  # Start from the first page if no file exists


def choose_p(list_p):
    if list_p != None:
        for p in list_p:
            try:
                if 'Download' in p.get_text() or 'Music' in p.get_text():
                    return p
            except:
                pass


def req(page_number):
    global headers
    response = requests.get(url + f'{page_number}', headers=headers)
    print(f'Status code for page {page_number}:', response.status_code)

    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = soup.find_all('div', {'class': 'posts'})[0]
            post_titr = posts.find_all('div', {'class': 'post-titr'})[0]
            p = post_titr.find_all('p')
            p = choose_p(p)
            music_name = p.get_text().split('Music')[0]

            # Save the song name to the file
            with open(output_file, 'a') as file:
                file.write(music_name + ',' + str(page_number) + '\n')

            # Save the last successfully scraped page
            save_last_page(page_number)

        except Exception as e:
            print(f"Error processing page {page_number}: {e}")


# Start scraping from the last saved page
start_page = load_last_page()

# Scrape pages in a loop with error handling
for i in range(start_page, 40000):
    try:
        req(i)
    except requests.exceptions.RequestException as e:
        print(f"Connection error on page {i}: {e}. Retrying in 1 seconds...")
        time.sleep(1)  # Wait 5 seconds before retrying
        continue
