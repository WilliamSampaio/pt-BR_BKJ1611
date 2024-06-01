import json

from unidecode import unidecode

from pt_br_bkj1611 import BASE_URL
from pt_br_bkj1611.functions import get_books_slug, get_soup

# import sys


# rename_files()
# print('oi!')
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

        with open(
            f'data/{str(book_index + 1).zfill(2)}_{chapter}.json', 'w'
        ) as f:
            f.write(json.dumps(data))
