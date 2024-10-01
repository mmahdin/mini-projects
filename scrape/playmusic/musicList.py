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
search_terms = [' melani ', ' kimia ', ' mehdi jahani ', ' diana ', ' parastoo ', ' satin ', 'masoud sadeghloo', 'ramyar', 'hamid askari', 'mehdi ahmadvand', 'mohsen yeganeh', 'mohsen lorestani', 'ebi', 'dariush', 'siavash ghomayshi', 'moein', 'hayedeh', 'mahasti', 'fataneh', 'googoosh', 'leila forouhar', 'andy', 'mohsen chavoshi', 'asraei', 'benyamin'
                ' baran ', ' shery m ', ' ستین ', ' از باران', ' پرستو ', ' دیانا ', ' شری ام ', ' کیمیا ', ' ملانی ', 'مسعود صادقلو', 'رامیار', 'حمید عسکری', 'مهدی احمدوند', 'محسن یگانه', 'محسن لرستانی', 'ابی', 'داریوش', 'سیاوش قمیشی', 'معین', 'هایده', 'مهستی', 'فتانه', 'گوگوش', 'لیلا فروهر', 'اندی', 'چاوشی', 'فریدون', 'بینامین']
file_names = ['/home/mahdi/Documents/mini-projects/scrape/playmusic/music-doni.txt',
              '/home/mahdi/Documents/mini-projects/scrape/playmusic/show-music.txt',
              '/home/mahdi/Documents/mini-projects/scrape/playmusic/sahand-music.txt']
urls = ['https://music-doni.ir/',
        'https://show-music.ir/', 'https://sahand-music.ir/']

res = get_search_items(
    search_terms, file_names[0], urls[0]) + get_search_items(search_terms, file_names[1], urls[1]) + get_search_items(search_terms, file_names[2], urls[2])

random.shuffle(res)
random.shuffle(res)
random.shuffle(res)

with open('/home/mahdi/Documents/mini-projects/scrape/playmusic/musicList.txt', 'w') as file:
    for i in res:
        file.write(i + '\n')
