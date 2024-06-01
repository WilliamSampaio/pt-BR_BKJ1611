import os
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup
from lxml import etree

from pt_br_bkj1611 import BASE_URL


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


def zip_bible(filename):
    with ZipFile(os.path.join(os.getcwd(), f'{filename}.zip'), 'w') as zip:
        for file in os.listdir('data'):
            zip.write(os.path.join('data', file))
    print(f'Bible {filename} zipped successfully!')
