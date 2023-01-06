import os
import requests
import urllib.request

from bs4 import BeautifulSoup
from tqdm import tqdm


BASE_URL = "https://mikucolle.gamerch.com"
CARD_PAGE = "https://mikucolle.gamerch.com/%E3%82%AB%E3%83%BC%E3%83%89%E4%B8%80%E8%A6%A7"
OUTPUT_FOLDER = "out"
MIKU = '''⠄⠄⠄⠄⠄⠄⣀⣀⠄⠄⠄⠄⣀⣀⣀⣀⣀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⣠⣤⠞⡋⠉⠧⠶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⢀⠏⠲⣄⠄⠄⠄⠄
⠄⢀⡴⠋⢁⢐⣵⣶⣿⠟⣛⣿⣿⣿⠿⢿⣿⣦⣝⡻⣿⢇⡟⠄⣠⣿⣿⣷⣦⡀
⠄⠸⢳⡜⢱⣿⣿⠛⡅⣿⣿⣿⡟⣱⣿⣦⡙⣿⣿⣿⡆⡜⠄⣀⢹⣿⣿⣿⣿⣿
⠄⢰⣧⢱⣿⣿⢃⠾⣃⢿⣿⣿⢰⣿⣿⣿⠳⠘⣿⣿⣦⡙⢤⡻⠸⡿⠿⣿⣿⣿
⠄⣿⡟⣼⣿⡏⣴⣿⣿⡜⣿⣿⢸⣿⣿⣿⣿⣷⠸⣿⣿⣿⢲⣙⢦⠄⠄⣼⣿⣿
⢸⣿⡇⣿⣿⡇⣿⡏⠈⣷⣜⢿⢸⣿⣿⡟⠈⣿⣆⢹⣿⣿⠄⠙⣷⠄⠄⣿⣿⣿
⣾⣿⡇⣿⣿⠃⣿⡇⠰⣿⣿⣶⣸⣿⣿⣇⠰⣿⣿⡆⣿⡟⠄⠄⡏⠄⢸⣿⣿⡟
⠟⣵⣦⢹⣿⢸⣿⣿⣶⣿⣿⣥⣿⣿⣿⣿⣶⣿⣿⡇⣿⡇⣀⣤⠃⠄⡀⠟⠋⠄
⡘⣿⡰⠊⠇⢾⣿⣿⣿⣿⣟⠻⣿⡿⣻⣿⣿⣿⣿⢃⡿⢰⡿⠋⠄⠄⠄⠄⣠⣾
⣿⣌⠵⠋⠈⠈⠻⢿⣿⣿⣿⣿⣶⣾⣿⣿⣿⣿⡇⠸⣑⡥⢂⣼⡷⠂⠄⢸⣿⣿
⣿⣿⡀⠄⠄⠄⠄⠄⢌⣙⡛⢛⠛⣛⠛⣛⢋⣥⡂⢴⡿⣱⣿⠟⠄⠄⠄⠘⣿⣿
⣿⣿⣿⣷⣦⣄⣀⣀⡼⡿⣷⡜⡗⠴⠸⠟⣼⡿⣴⡓⢎⣛⠁⠄⠄⠄⠄⠄⢿⣿
⣿⣿⣿⣿⣿⣿⠄⠙⠻⢧⣿⣿⡜⣼⢸⣎⣭⣹⢸⡿⣣⠞⢷⡀⠄⠄⠄⠄⢸⣿
⣿⣿⣿⣿⣿⣿⠄⠄⠄⠄⣿⣿⡇⣿⢸⣿⣿⣿⡗⢨⠁⠄⠄⢳⡄⠄⠄⠄⢸⣿'''


def download_html(page):
    req = requests.get(page)
    if req.status_code == 200:
        resp = req.text
        return resp
    return None


def extract_urls(html):
    urls = []

    bs = BeautifulSoup(html, "html.parser")
    table = bs.find("table").tbody

    for tr in table.find_all("tr"):
        td = tr.find("td", {"data-col": "4"})
        link = td.find("a")

        full_path = BASE_URL + link['href']
        urls.append(full_path)

    return urls


def download_images(url_list):
    for url in tqdm(url_list):
        html = download_html(url)

        if html is not None:
            bs = BeautifulSoup(html, "html.parser")

            # image link
            image = bs.find("img", {"class": "ui_wikidb_main_img"})
            image_url = image['src']

            # character
            character = bs.select_one('.ui_wikidb_top_pc > p:nth-child(2) > span:nth-child(1)')
            next_elem = character.findNext()
            if next_elem.name == "a":
                character_name = next_elem['title'].strip()
            else:
                character_name = next_elem.previous_sibling.text.strip()

            # card name
            card_name = bs.find("h2", {"id": "js_wikidb_main_name"})

            # output path
            filename = f"{card_name.text.strip()}.jpg"
            character_dir = os.path.join(OUTPUT_FOLDER, character_name)
            if not os.path.exists(character_dir):
                os.makedirs(character_dir, exist_ok=True)
            output_file = os.path.join(character_dir, filename)

            urllib.request.urlretrieve(image_url, filename=output_file)


def main():
    print("MikuColle scraper!")
    print(MIKU)
    print()
    print("downloading main page")
    html = download_html(CARD_PAGE)
    print("extracting card urls")
    urls = extract_urls(html)
    print("downloading card images")
    download_images(urls)
    print("done!")


if __name__ == '__main__':
    main()
