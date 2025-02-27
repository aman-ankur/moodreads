import pytest
from moodreads.scraper.goodreads import GoodreadsScraper

def test_scraper_initialization():
    scraper = GoodreadsScraper()
    assert scraper is not None

def test_scrape_book():
    scraper = GoodreadsScraper()
    book_url = "https://www.goodreads.com/book/show/40121378-atomic-habits"
    
    book_data = scraper.scrape_book(book_url)
    assert isinstance(book_data, dict)
    assert 'title' in book_data
    assert 'author' in book_data 