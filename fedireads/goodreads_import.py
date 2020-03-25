import re
import csv
import itertools
from requests import HTTPError

from fedireads import books_manager

def unquote_string(text):
    match = re.match(r'="([^"]*)"', text)
    if match:
        return match.group(1)
    else:
        return text

def construct_search_term(title, author):
    # Strip brackets (usually series title from search term)
    title = re.sub(r'\s*\([^)]*\)\s*', '', title)
    # Open library doesn't like including author initials in search term.
    author = re.sub(r'(\w\.)+\s*', '', author)

    return ' '.join([title, author])

class GoodreadsCsv(object):
    def __init__(self, csv_file):
        self.reader = csv.DictReader(csv_file)

    def __iter__(self):
        for line in itertools.islice(self.reader, 20, 30):
            entry = GoodreadsItem(line)
            try:
                entry.resolve()
            except HTTPError:
                pass
            yield entry

class GoodreadsItem(object):
    def __init__(self, line):
        self.line = line
        self.book = None

    def resolve(self):
        self.book = self.get_book_from_isbn()
        if not self.book:
            self.book = self.get_book_from_title_author()

    def get_book_from_isbn(self):
        isbn = unquote_string(self.line['ISBN13'])
        search_results = books_manager.search(isbn)
        if search_results:
            return books_manager.get_or_create_book(search_results[0].key)

    def get_book_from_title_author(self):
        search_term = construct_search_term(self.line['Title'], self.line['Author'])
        search_results = books_manager.search(search_term)
        if search_results:
            return books_manager.get_or_create_book(search_results[0].key)

    def __repr__(self):
        return "<GoodreadsItem {!r}>".format(self.line['Title'])
