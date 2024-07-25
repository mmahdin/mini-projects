import requests
from bs4 import BeautifulSoup

# URL of the Amazon.es Books page
url = 'https://www.amazon.es/s?k=books&crid=1OKX7WXE69TGP&sprefix=books%2Caps%2C892&ref=nb_sb_ss_pltr-data-refreshed_1_5'

# Send a request to the URL
costum_headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36', 'accept-language': 'en,en-GB;q=0.9,fa-IR;q=0.8,fa;q=0.7,en-US;q=0.6'}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

print(response.status_code)

base_addr = 'https://www.amazon.es'


####################### find books categories and their links ######################

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize an empty dictionary to store the words and links
    word_link_dict = {}

    # Find all the outer spans
    outer_spans = []
    outer_spans.append(soup.find_all(
        'span', {'data-csa-c-type': 'element', 'data-csa-c-content-id': "n/599364031"})[0])
    outer_spans.append(soup.find_all(
        'span', {'data-csa-c-type': 'element', 'data-csa-c-content-id': "n/818936031"})[0])
    for outer_span in outer_spans:
        # Find all the li elements within each outer span
        li_elements = outer_span.find_all('li')

        for li in li_elements:
            # Find the <a> tag within each li
            a_tag = li.find('a')
            if a_tag:
                # Extract the href attribute (link)
                link = a_tag['href']
                # Find the <span> within the <a> tag
                inner_span = a_tag.find('span')
                if inner_span:
                    # Get the text within the <font>
                    word = inner_span.get_text(strip=True)
                    # Store the word and link in the dictionary
                    if (word != ''):
                        word_link_dict[word] = base_addr + link
print(word_link_dict.keys())
print("Extract link of books category done")


def func(key, link, tree):
    print("\nKey: ", key)
    tree.append(key)
    libros_link = link
    response = requests.get(libros_link, headers=headers)
    print(response.status_code)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        word_link_dict = {}
        outer_spans = soup.find_all(
            'span', {'data-csa-c-type': 'element', 'data-csa-c-content-id': "n/599364031"})[0]
        li_elements = outer_spans.find_all('li')
        for li in li_elements:
            a_tag = li.find('a')
            if a_tag:
                link = a_tag['href']
                inner_span = a_tag.find('span')
                if inner_span:
                    word = inner_span.get_text(strip=True)
                    if (word != ''):
                        word_link_dict[word] = base_addr + link
    if len(list(word_link_dict.keys())) == 0:
        print("\n\nfinish with key:", key)
        write2csv(tree, libros_link)
        return
    print(word_link_dict.keys())
    func(list(word_link_dict.keys())[
        0], word_link_dict[list(word_link_dict.keys())[0]], tree)


file_name = 0


def write2csv(tree, link):
    global file_name, headers, base_addr
    response = requests.get(link, headers=headers)
    print("in write2csv function")
    print(response.status_code)
    names = []
    bsrs = []
    prices = []
    if response.status_code == 200:
        links = find_link_of_books(response)
        for link in links:
            response = requests.get(link, headers=headers)
            print('\nrequest to each books. status:', response.status_code)
            if response.status_code == 200:
                # get name of books
                names.append(find_names(response).replace(',', ' | '))

                # get bsrs of books
                bsr = find_bsrs(response)
                if len(bsr) == 0:
                    bsrs.append('None')
                else:
                    bsrs.append(bsr)

                # get price of books
                price = find_price(response)
                if price == '':
                    prices.append('None')
                else:
                    prices.append(price.replace(',', '.'))

    file_path = f'{file_name}.csv'
    with open(file_path, "w") as file:
        # write categories
        for string in tree:
            file.write(string + "\n")

        for i in range(len(names)):
            # write name of book
            file.write(names[i] + ",")

            # write bsr of book (if exist)
            if bsrs[i] == 'None':
                file.write('None,')
            else:
                for b in bsrs[i]:
                    file.write(b + ' | ')
                file.write(',')

            # write price
            file.write(prices[i]+',')

            file.write('\n')
    file_name += 1


def find_link_of_books(response):
    NUM_BOOKS = 2
    global base_addr, headers
    links = []

    soup = BeautifulSoup(response.content, 'html.parser')
    # outer_divs = soup.find_all(
    #     'div', {'data-component-type': "s-search-result"})
    # outer_as = soup.find_all(
    #     'a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
    h2s = soup.find_all(
        'h2', {'class', 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'})
    for h2 in h2s:
        a_tag = h2.find('a', {
                        'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        link = a_tag['href']
        links.append(base_addr + link)
        if len(links) == NUM_BOOKS:
            return links

    next_page_link = soup.find_all(
        'a', {'class': "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"})[0]
    next_page_link = base_addr + next_page_link['href']

    while len(links) < NUM_BOOKS:
        response = requests.get(next_page_link, headers=headers)
        print('\nfind link of book. status: ', response.status_code)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            h2s = soup.find_all(
                'h2', {'class', 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'})

            for h2 in h2s:
                a_tag = h2.find('a', {
                                'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
                link = a_tag['href']
                links.append(base_addr + link)
                if len(links) == NUM_BOOKS:
                    return links


def find_names(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    outer = soup.find_all('span', {'id': "productTitle"})[0]
    title = outer.get_text(strip=True)
    return title


def find_bsrs(response):
    print('\n', 'in find_bsrs\n')
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main div
    div = soup.find('div', {'id': 'detailBulletsWrapper_feature_div'})
    if not div:
        print("Div with id 'detailBulletsWrapper_feature_div' not found")
        return []

    # Find the ul with the specified class within the div
    ul = div.find_all('ul', {
        'class': "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"})[1]
    if not ul:
        print("UL with the specified class not found")
        return []

    nested_ul = ul.find(
        'ul', {'class': "a-unordered-list a-nostyle a-vertical zg_hrsr"})
    if not nested_ul:
        print("nested UL with the specified class not found")
        return []

    # Find all li elements within the nested ul
    lis = nested_ul.find_all('li')
    if not lis:
        print("No li elements found within the nested ul")
        return []

    res = []

    # Loop through each li element and extract text
    for li in lis:
        # Extract text from the first font element
        span = li.find('span', {'class': "a-list-item"})
        if not span:
            print('span')
            continue
        txt = span.get_text()

        a = span.find('a')
        if not a:
            print('a')
            continue

        txt += " " + a.get_text()
        res.append(txt)

    return res


def find_price(response):
    print('\n', 'in find_price\n')
    soup = BeautifulSoup(response.content, 'html.parser')

    right_div = soup.find('div', {'id': 'rightCol'})
    if not right_div:
        print("right_div not found")
        return ''

    div = right_div.find('div', {'id': "corePriceDisplay_desktop_feature_div",
                                 'class': "celwidget", 'data-feature-name': "corePriceDisplay_desktop"})
    if not div:
        print("div (corePriceDisplay_desktop_feature_div) not found")
        return ''

    div = div.find(
        'div', {'class': "a-section a-spacing-none aok-align-center aok-relative"})
    if not div:
        print("div (a-section a-spacing-none) not found")
        return ''

    span = div.find('span', {
                    'class': "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"})
    if not span:
        print("span not found")
        return ''

    txt = soup.find('span', class_='a-price-whole').text
    txt += soup.find('span', class_='a-price-fraction').text
    txt += soup.find('span', class_='a-price-symbol').text

    return txt


for name in list(word_link_dict.keys()):
    tree = []
    func(name, word_link_dict[name], tree)
