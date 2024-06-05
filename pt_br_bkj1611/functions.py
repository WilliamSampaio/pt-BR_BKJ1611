import json
import os
from datetime import datetime
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup
from lxml import etree

from pt_br_bkj1611 import BASE_URL, USER_AGENT


def http_request(url: str):
    req = None
    try:
        req = requests.get(
            url,
            headers={'User-Agent': USER_AGENT},
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


def write_index():
    if os.path.exists(os.path.join('data', '00.json')):
        index = None
        with open(os.path.join('data', '00.json')) as f:
            index = json.load(f)
    else:
        index = {
            'bible': '',
            'slug': '',
            'lang': '',
            'url_from': BASE_URL,
            'scraping_date': None,
        }
    filenames = os.listdir('data')
    filenames.sort()
    index['books'] = {}
    for filename in filenames:
        if filename == '00.json':
            continue
        if filename.split('_')[0] in index['books']:
            continue
        with open(os.path.join('data', filename)) as f:
            data = json.load(f)
            index['books'][filename.split('_')[0]] = data['book']
    with open(os.path.join('data', '00.json'), 'w') as f:
        index['scraping_date'] = datetime.today().strftime('%Y-%m-%d')
        f.write(json.dumps(index, indent=4))


def zip_bible(filename):
    with ZipFile(os.path.join(os.getcwd(), f'{filename}.zip'), 'w') as zip:
        for file in os.listdir('data'):
            zip.write(os.path.join('data', file))
    print(f'Bible {filename} zipped successfully!')
