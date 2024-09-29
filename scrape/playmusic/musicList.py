import random


def get_search_items(search_terms, file_name, url):
    second_elements = []
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            line_lower = line.lower()
            if any(term in line_lower for term in search_terms):
                parts = line.split(',')
                if len(parts) > 1:
                    second_elements.append(url + str(parts[1].strip()))
    return second_elements


# Define the search list
search_terms = ['melani', 'kimia', 'mehdi jahani', 'diana', 'Parastoo', 'satin',
                'baran', 'shery m', 'ستین', 'از باران', 'پرستو', 'دیانا', 'شری ام', 'کیمیا', 'ملانی']
file_names = ['/home/mahdi/Documents/mini-projects/scrape/playmusic/music-doni.txt',
              '/home/mahdi/Documents/mini-projects/scrape/playmusic/show-music.txt']
urls = ['https://music-doni.ir/', 'https://show-music.ir/']

res = get_search_items(
    search_terms, file_names[0], urls[0]) + get_search_items(search_terms, file_names[1], urls[1])

random.shuffle(res)
random.shuffle(res)
random.shuffle(res)

with open('/home/mahdi/Documents/mini-projects/scrape/playmusic/musicList.txt', 'w') as file:
    for i in res:
        file.write(i + '\n')
