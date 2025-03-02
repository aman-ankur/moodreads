#!/usr/bin/env python3
"""
Unit tests for the AdvancedBookScraper class.

This module contains tests to verify the functionality of the AdvancedBookScraper class,
ensuring that it correctly scrapes book data, processes batches, and handles errors.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_books import AdvancedBookScraper
from moodreads.scraper.goodreads import GoodreadsScraper

class TestAdvancedBookScraper(unittest.TestCase):
    """Test cases for the AdvancedBookScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the MongoDB client
        self.db_patcher = patch('scripts.scrape_books.MongoDBClient')
        self.mock_db = self.db_patcher.start()
        self.mock_db_instance = self.mock_db.return_value
        self.mock_db_instance.books_collection = MagicMock()
        
        # Create a mock for the GoodreadsScraper
        self.scraper_patcher = patch('scripts.scrape_books.GoodreadsScraper')
        self.mock_scraper = self.scraper_patcher.start()
        self.mock_scraper_instance = self.mock_scraper.return_value
        
        # Create a mock for the EmotionalAnalyzer
        self.analyzer_patcher = patch('scripts.scrape_books.EmotionalAnalyzer')
        self.mock_analyzer = self.analyzer_patcher.start()
        self.mock_analyzer_instance = self.mock_analyzer.return_value
        
        # Create a mock for requests
        self.requests_patcher = patch('scripts.scrape_books.requests')
        self.mock_requests = self.requests_patcher.start()
        
        # Create the AdvancedBookScraper instance
        self.scraper = AdvancedBookScraper(
            batch_size=2,
            rate_limit=0.0,  # No rate limiting for tests
            progress_file="test_progress.json",
            db_name="test_db",
            skip_emotional_analysis=True
        )
        
        # Replace the real instances with mocks
        self.scraper.db = self.mock_db_instance
        self.scraper.scraper = self.mock_scraper_instance
        self.scraper.analyzer = self.mock_analyzer_instance
        
        # Sample book data
        self.sample_book = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890",
            "url": "https://www.goodreads.com/book/show/12345",
            "rating": 4.5,
            "cover_image": "https://example.com/cover.jpg",
            "genres": ["Fiction", "Science Fiction"]
        }
        
        # Sample Google Books data
        self.sample_google_data = {
            "google_id": "abcdef123456",
            "google_title": "Test Book: A Novel",
            "google_authors": ["Test Author"],
            "google_description": "A test book description.",
            "google_categories": ["Fiction", "Science Fiction"],
            "google_rating": 4.2,
            "google_image_links": {
                "thumbnail": "https://example.com/thumbnail.jpg",
                "small": "https://example.com/small.jpg",
                "medium": "https://example.com/medium.jpg",
                "large": "https://example.com/large.jpg"
            }
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.db_patcher.stop()
        self.scraper_patcher.stop()
        self.analyzer_patcher.stop()
        self.requests_patcher.stop()
    
    @patch('scripts.scrape_books.json.load')
    @patch('scripts.scrape_books.open', new_callable=mock_open)
    def test_load_progress(self, mock_file, mock_json_load):
        """Test loading progress from a file."""
        # Set up mock return value
        mock_json_load.return_value = {
            "processed_urls": ["https://example.com/book/1", "https://example.com/book/2"],
            "last_updated": "2023-01-01T00:00:00"
        }
        
        # Set up mock for Path.exists
        with patch('scripts.scrape_books.Path.exists', return_value=True):
            # Call the method
            self.scraper.load_progress()
        
        # Check if the file was opened correctly
        mock_file.assert_called_once_with(self.scraper.progress_file)
        
        # Check if the processed URLs were loaded
        self.assertEqual(len(self.scraper.processed_urls), 2)
        self.assertIn("https://example.com/book/1", self.scraper.processed_urls)
        self.assertIn("https://example.com/book/2", self.scraper.processed_urls)
    
    @patch('scripts.scrape_books.json.dump')
    @patch('scripts.scrape_books.open', new_callable=mock_open)
    def test_save_progress(self, mock_file, mock_json_dump):
        """Test saving progress to a file."""
        # Set up test data
        self.scraper.processed_urls = {"https://example.com/book/1", "https://example.com/book/2"}
        
        # Call the method
        self.scraper.save_progress()
        
        # Check if the file was opened correctly
        mock_file.assert_called_once_with(self.scraper.progress_file, 'w')
        
        # Check if json.dump was called with the correct data
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        self.assertEqual(len(args[0]["processed_urls"]), 2)
        self.assertIn("https://example.com/book/1", args[0]["processed_urls"])
        self.assertIn("https://example.com/book/2", args[0]["processed_urls"])
        self.assertIn("last_updated", args[0])
    
    def test_get_category_urls(self):
        """Test getting book URLs for a category."""
        # Set up mock return value
        self.mock_scraper_instance.get_book_urls_from_page.return_value = [
            "https://www.goodreads.com/book/show/1",
            "https://www.goodreads.com/book/show/2"
        ]
        
        # Call the method
        urls = self.scraper.get_category_urls("fiction", depth=1)
        
        # Check if the scraper method was called correctly
        self.mock_scraper_instance.get_book_urls_from_page.assert_called_once()
        
        # Check if the correct URLs were returned
        self.assertEqual(len(urls), 2)
        self.assertIn("https://www.goodreads.com/book/show/1", urls)
        self.assertIn("https://www.goodreads.com/book/show/2", urls)
    
    def test_get_google_books_data_with_isbn(self):
        """Test getting Google Books data with ISBN."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{
                "id": "abcdef123456",
                "volumeInfo": {
                    "title": "Test Book: A Novel",
                    "authors": ["Test Author"],
                    "description": "A test book description.",
                    "categories": ["Fiction", "Science Fiction"],
                    "averageRating": 4.2,
                    "imageLinks": {
                        "thumbnail": "https://example.com/thumbnail.jpg",
                        "smallThumbnail": "https://example.com/small.jpg"
                    }
                }
            }]
        }
        self.mock_requests.get.return_value = mock_response
        
        # Call the method
        result = self.scraper.get_google_books_data("Test Book", "Test Author", isbn="1234567890")
        
        # Check if the request was made correctly
        self.mock_requests.get.assert_called_once()
        args, kwargs = self.mock_requests.get.call_args
        self.assertIn("isbn:1234567890", args[0])
        
        # Check the result
        self.assertEqual(result["google_id"], "abcdef123456")
        self.assertEqual(result["google_title"], "Test Book: A Novel")
        self.assertEqual(result["google_authors"], ["Test Author"])
        self.assertEqual(result["google_rating"], 4.2)
    
    def test_get_google_books_data_with_title_author(self):
        """Test getting Google Books data with title and author."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{
                "id": "abcdef123456",
                "volumeInfo": {
                    "title": "Test Book: A Novel",
                    "authors": ["Test Author"],
                    "description": "A test book description.",
                    "categories": ["Fiction", "Science Fiction"],
                    "averageRating": 4.2,
                    "imageLinks": {
                        "thumbnail": "https://example.com/thumbnail.jpg",
                        "smallThumbnail": "https://example.com/small.jpg"
                    }
                }
            }]
        }
        self.mock_requests.get.return_value = mock_response
        
        # Call the method
        result = self.scraper.get_google_books_data("Test Book", "Test Author")
        
        # Check if the request was made correctly
        self.mock_requests.get.assert_called_once()
        args, kwargs = self.mock_requests.get.call_args
        self.assertIn("intitle:Test+Book", args[0])
        self.assertIn("inauthor:Test+Author", args[0])
        
        # Check the result
        self.assertEqual(result["google_id"], "abcdef123456")
        self.assertEqual(result["google_title"], "Test Book: A Novel")
        self.assertEqual(result["google_authors"], ["Test Author"])
        self.assertEqual(result["google_rating"], 4.2)
    
    def test_get_google_books_data_no_results(self):
        """Test getting Google Books data with no results."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No items
        self.mock_requests.get.return_value = mock_response
        
        # Call the method
        result = self.scraper.get_google_books_data("Test Book", "Test Author")
        
        # Check if the request was made correctly
        self.mock_requests.get.assert_called_once()
        
        # Check the result
        self.assertEqual(result, {})
    
    def test_get_google_books_data_error(self):
        """Test getting Google Books data with an error."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        self.mock_requests.get.return_value = mock_response
        
        # Call the method
        result = self.scraper.get_google_books_data("Test Book", "Test Author")
        
        # Check if the request was made correctly
        self.mock_requests.get.assert_called_once()
        
        # Check the result
        self.assertEqual(result, {})
    
    def test_scrape_basic_book_data(self):
        """Test scraping basic book data."""
        # Set up mock return value
        self.mock_scraper_instance.scrape_book.return_value = self.sample_book
        
        # Call the method
        result = self.scraper.scrape_basic_book_data("https://www.goodreads.com/book/show/12345", skip_reviews=True)
        
        # Check if the scraper method was called correctly
        self.mock_scraper_instance.scrape_book.assert_called_once_with("https://www.goodreads.com/book/show/12345", skip_quotes=True)
        
        # Check the result
        self.assertEqual(result["title"], "Test Book")
        self.assertEqual(result["author"], "Test Author")
        self.assertEqual(result["isbn"], "1234567890")
    
    def test_scrape_basic_book_data_missing_title(self):
        """Test scraping basic book data with missing title."""
        # Set up mock return value with missing title
        book_data = self.sample_book.copy()
        book_data["title"] = ""
        self.mock_scraper_instance.scrape_book.return_value = book_data
        
        # Set up mock for _extract_title_from_url
        with patch.object(self.scraper, '_extract_title_from_url', return_value="Extracted Title"):
            # Call the method
            result = self.scraper.scrape_basic_book_data("https://www.goodreads.com/book/show/12345-test-book", skip_reviews=True)
            
            # Check if the title was extracted from the URL
            self.scraper._extract_title_from_url.assert_called_once_with("https://www.goodreads.com/book/show/12345-test-book")
            
            # Check the result
            self.assertEqual(result["title"], "Extracted Title")
    
    def test_extract_title_from_url(self):
        """Test extracting title from URL."""
        # Test with standard URL format
        url = "https://www.goodreads.com/book/show/12345-test-book-title"
        title = self.scraper._extract_title_from_url(url)
        self.assertEqual(title, "Test Book Title")
        
        # Test with URL without title
        url = "https://www.goodreads.com/book/show/12345"
        title = self.scraper._extract_title_from_url(url)
        self.assertEqual(title, "")
    
    def test_extract_book_id(self):
        """Test extracting book ID from URL."""
        # Test with standard URL format
        url = "https://www.goodreads.com/book/show/12345-test-book"
        book_id = self.scraper._extract_book_id(url)
        self.assertEqual(book_id, "12345")
        
        # Test with URL without ID
        url = "https://www.goodreads.com/book/show/"
        book_id = self.scraper._extract_book_id(url)
        self.assertEqual(book_id, "")
    
    @patch.object(AdvancedBookScraper, 'get_google_books_data')
    @patch.object(AdvancedBookScraper, 'scrape_basic_book_data')
    def test_process_batch(self, mock_scrape_basic, mock_get_google):
        """Test processing a batch of book URLs."""
        # Set up mock return values
        mock_scrape_basic.return_value = self.sample_book
        mock_get_google.return_value = self.sample_google_data
        
        # Set up mock for database
        self.mock_db_instance.books_collection.find_one.return_value = None  # Book not in database
        
        # Call the method
        self.scraper.process_batch(["https://www.goodreads.com/book/show/12345"], batch_num=1)
        
        # Check if the methods were called correctly
        mock_scrape_basic.assert_called_once()
        mock_get_google.assert_called_once_with("Test Book", "Test Author", isbn="1234567890")
        
        # Check if the book was added to the database
        self.mock_db_instance.books_collection.insert_one.assert_called_once()
    
    @patch.object(AdvancedBookScraper, 'get_google_books_data')
    @patch.object(AdvancedBookScraper, 'scrape_basic_book_data')
    def test_process_batch_missing_title(self, mock_scrape_basic, mock_get_google):
        """Test processing a batch with missing title."""
        # Set up mock return value with missing title
        book_data = self.sample_book.copy()
        book_data["title"] = ""
        mock_scrape_basic.return_value = book_data
        
        # Call the method
        self.scraper.process_batch(["https://www.goodreads.com/book/show/12345"], batch_num=1)
        
        # Check if the Google Books API was not called
        mock_get_google.assert_not_called()
        
        # Check if the book was not added to the database
        self.mock_db_instance.books_collection.insert_one.assert_not_called()
    
    @patch.object(AdvancedBookScraper, 'get_google_books_data')
    @patch.object(AdvancedBookScraper, 'scrape_basic_book_data')
    def test_process_batch_missing_author(self, mock_scrape_basic, mock_get_google):
        """Test processing a batch with missing author."""
        # Set up mock return value with missing author
        book_data = self.sample_book.copy()
        book_data["author"] = ""
        mock_scrape_basic.return_value = book_data
        
        # Set up Google Books data with author
        google_data = self.sample_google_data.copy()
        mock_get_google.return_value = google_data
        
        # Call the method
        self.scraper.process_batch(["https://www.goodreads.com/book/show/12345"], batch_num=1)
        
        # Check if the Google Books API was called
        mock_get_google.assert_called_once_with("Test Book", "", isbn="1234567890")
        
        # Check if the book was added to the database with the author from Google Books
        self.mock_db_instance.books_collection.insert_one.assert_called_once()
        args, _ = self.mock_db_instance.books_collection.insert_one.call_args
        self.assertEqual(args[0]["author"], "Test Author")  # Author from Google Books
    
    @patch.object(AdvancedBookScraper, 'get_google_books_data')
    @patch.object(AdvancedBookScraper, 'scrape_basic_book_data')
    def test_process_batch_already_processed(self, mock_scrape_basic, mock_get_google):
        """Test processing a batch with already processed URL."""
        # Add URL to processed_urls
        self.scraper.processed_urls.add("https://www.goodreads.com/book/show/12345")
        
        # Call the method
        self.scraper.process_batch(["https://www.goodreads.com/book/show/12345"], batch_num=1)
        
        # Check if the scraper method was not called
        mock_scrape_basic.assert_not_called()
        
        # Check if the Google Books API was not called
        mock_get_google.assert_not_called()
        
        # Check if the book was not added to the database
        self.mock_db_instance.books_collection.insert_one.assert_not_called()
    
    @patch.object(AdvancedBookScraper, 'get_google_books_data')
    @patch.object(AdvancedBookScraper, 'scrape_basic_book_data')
    def test_process_batch_already_in_database(self, mock_scrape_basic, mock_get_google):
        """Test processing a batch with book already in database."""
        # Set up mock return values
        mock_scrape_basic.return_value = self.sample_book
        mock_get_google.return_value = self.sample_google_data
        
        # Set up mock for database to indicate book exists
        self.mock_db_instance.books_collection.find_one.return_value = {"_id": "existing_id", "title": "Test Book"}
        
        # Initialize empty set for processed_urls
        self.scraper.processed_urls = set()
        
        # Call the method
        self.scraper.process_batch(["https://www.goodreads.com/book/show/12345"], batch_num=1)
        
        # Check if the URL was added to processed_urls
        self.assertIn("https://www.goodreads.com/book/show/12345", self.scraper.processed_urls)
        
        # Check if the database find_one method was called with the correct query
        self.mock_db_instance.books_collection.find_one.assert_called_once_with({"goodreads_id": "12345"})
        
        # Check if the book was not added to the database
        self.mock_db_instance.books_collection.insert_one.assert_not_called()

    def test_script_calls_process_batch_correctly(self):
        """Test that the test_advanced_scraper.py script calls process_batch with the correct parameters."""
        # Create a mock for the AdvancedBookScraper class
        with patch('scripts.test_advanced_scraper.AdvancedBookScraper') as mock_scraper_class:
            # Create a mock instance
            mock_scraper = mock_scraper_class.return_value
            
            # Set up the get_category_urls method to return a list of URLs
            mock_scraper.get_category_urls.return_value = ['url1', 'url2']
            
            # Import the test function
            from scripts.test_advanced_scraper import test_scraper
            
            # Call the test function
            test_scraper('test-category', 2, 'test-db')
            
            # Check that process_batch was called with the correct parameters
            # It should be called twice, once for each URL
            assert mock_scraper.process_batch.call_count == 2
            
            # Check the first call
            args1, kwargs1 = mock_scraper.process_batch.call_args_list[0]
            assert args1[0] == ['url1']  # First argument should be a list with the URL
            assert 'batch_num' in kwargs1 or len(args1) > 1  # batch_num should be provided
            
            # Check the second call
            args2, kwargs2 = mock_scraper.process_batch.call_args_list[1]
            assert args2[0] == ['url2']  # First argument should be a list with the URL
            assert 'batch_num' in kwargs2 or len(args2) > 1  # batch_num should be provided

if __name__ == "__main__":
    unittest.main() 