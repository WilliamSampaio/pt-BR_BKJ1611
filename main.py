import json
import os

import requests
from bs4 import BeautifulSoup
from lxml import etree
from unidecode import unidecode

# import sys


BASE_URL = 'https://bkjfiel.com.br/'


def http_request(url: str):
    req = None
    try:
        req = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                + 'Chrome/125.0.0.0 Safari/537.36'
            },
        )
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    if req.status_code != 200:
        return None
    return req


def get_dom(url):
    req = http_request(url)
    if req is None:
        return None
    try:
        soup = BeautifulSoup(req.content, 'html.parser')
        return etree.HTML(str(soup))
    except Exception as e:
        print(e)
        return None


def get_soup(url):
    req = http_request(url)
    if req is None:
        return None
    try:
        return BeautifulSoup(req.content, 'html.parser')
    except Exception as e:
        print(e)
        return None


def get_books_slug() -> list:
    dom = get_dom(BASE_URL)
    if dom is None:
        return None
    try:
        el = dom.xpath(
            '//*[@id="app"]/header/div[3]/div/div/label/select//option'
        )
        return [str(e.text) for e in el]
    except Exception as e:
        raise e


def rename_files():
    for filename in os.listdir('data'):
        if len(filename.split('_')[0]) == 2:
            continue
        new_filename = '_'.join(
            [str(filename.split('_')[0]).zfill(2), filename.split('_')[1]]
        )
        os.rename(f'data/{filename}', f'data/{new_filename}')


if __name__ == '__main__':

    # rename_files()
    # sys.exit()

    books = get_books_slug()
    if books is None:
        raise Exception

    for book_index in range(0, len(books)):

        for chapter in range(1, 151):

            data = {
                'book': books[book_index],
                'chapter': chapter,
                'verses': [],
            }

            soup = get_soup(
                BASE_URL
                + '{}-{}'.format(
                    unidecode(books[book_index]).lower().replace(' ', '-'),
                    str(chapter),
                )
            )

            if soup is None:
                break

            verses = (
                soup.find(attrs={'id': 'main'})
                .find('section', attrs={'class': 'container'})
                .find('div')
                .find_all('div')[2]
                .find_all('a')
            )

            for verse in verses:
                data['verses'].append(
                    ''.join([str(a) for a in list(verse)[2:]])
                    .strip()
                    .replace(' </em>', '</em> ')
                )

            with open(f'data/{book_index + 1}_{chapter}.json', 'w') as f:
                f.write(json.dumps(data))
