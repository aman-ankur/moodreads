#!/usr/bin/env python3
"""
Test script to verify the fixes for the process_batch method in the AdvancedBookScraper class.

This script tests the process_batch method with a single URL to ensure it works correctly.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_books import AdvancedBookScraper

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_process_batch():
    """Test the process_batch method with a single URL."""
    try:
        # Create a temporary directory for progress file
        Path("temp").mkdir(exist_ok=True)
        
        # Initialize the scraper with test settings
        scraper = AdvancedBookScraper(
            batch_size=1,
            rate_limit=0.1,  # Minimal rate limiting for testing
            progress_file="temp/test_progress.json",
            db_name="moodreads_test",
            skip_emotional_analysis=True  # Skip emotional analysis for faster testing
        )
        
        # Test URL - use a well-known book
        test_url = "https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye"
        
        logger.info(f"Testing process_batch with URL: {test_url}")
        
        # Call the process_batch method with batch_num parameter
        scraper.process_batch([test_url], batch_num=1)
        
        # Verify that the URL was processed
        logger.info(f"Processed URLs: {scraper.processed_urls}")
        assert test_url in scraper.processed_urls, "URL was not processed"
        
        logger.info("Test passed: process_batch method works correctly with batch_num parameter")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_extract_title_from_url():
    """Test the _extract_title_from_url method with different URL formats."""
    try:
        # Initialize the scraper with test settings
        scraper = AdvancedBookScraper(
            batch_size=1,
            rate_limit=0.1,
            progress_file="temp/test_progress.json",
            db_name="moodreads_test",
            skip_emotional_analysis=True
        )
        
        # Test URLs
        test_urls = [
            ("https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye", "The Catcher In The Rye"),
            ("https://www.goodreads.com/book/show/12345-test-book-title", "Test Book Title"),
            ("https://www.goodreads.com/book/show/12345_test_book_title", "Test Book Title"),
            ("https://www.goodreads.com/book/show/12345", "")
        ]
        
        for url, expected_title in test_urls:
            title = scraper._extract_title_from_url(url)
            logger.info(f"URL: {url}, Extracted title: {title}, Expected: {expected_title}")
            
            # Check if the title matches the expected title
            if expected_title:
                assert title.lower() == expected_title.lower(), f"Title mismatch: {title} != {expected_title}"
            else:
                assert title == "", "Title should be empty"
        
        logger.info("Test passed: _extract_title_from_url method works correctly")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_extract_book_id():
    """Test the _extract_book_id method with different URL formats."""
    try:
        # Initialize the scraper with test settings
        scraper = AdvancedBookScraper(
            batch_size=1,
            rate_limit=0.1,
            progress_file="temp/test_progress.json",
            db_name="moodreads_test",
            skip_emotional_analysis=True
        )
        
        # Test URLs
        test_urls = [
            ("https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye", "5107"),
            ("https://www.goodreads.com/book/show/12345-test-book-title", "12345"),
            ("https://www.goodreads.com/book/show/12345_test_book_title", "12345"),
            ("https://www.goodreads.com/book/show/", "")
        ]
        
        for url, expected_id in test_urls:
            book_id = scraper._extract_book_id(url)
            logger.info(f"URL: {url}, Extracted ID: {book_id}, Expected: {expected_id}")
            
            # Check if the ID matches the expected ID
            assert book_id == expected_id, f"ID mismatch: {book_id} != {expected_id}"
        
        logger.info("Test passed: _extract_book_id method works correctly")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_get_google_books_data():
    """Test the get_google_books_data method with different parameters."""
    try:
        # Initialize the scraper with test settings
        scraper = AdvancedBookScraper(
            batch_size=1,
            rate_limit=0.1,
            progress_file="temp/test_progress.json",
            db_name="moodreads_test",
            skip_emotional_analysis=True
        )
        
        # Test cases
        test_cases = [
            # (title, author, isbn, should_have_data)
            ("The Catcher in the Rye", "J.D. Salinger", "", True),
            ("1984", "George Orwell", "9780451524935", True),
            ("", "", "", False),  # Empty parameters
            ("NonexistentBookTitle12345", "NonexistentAuthor12345", "", False)  # Nonexistent book
        ]
        
        for title, author, isbn, should_have_data in test_cases:
            logger.info(f"Testing get_google_books_data with title='{title}', author='{author}', isbn='{isbn}'")
            data = scraper.get_google_books_data(title, author, isbn)
            
            if should_have_data:
                assert data, f"Expected data for {title} by {author}, but got none"
                logger.info(f"Got data: {list(data.keys())}")
            else:
                assert not data, f"Expected no data for {title} by {author}, but got {data}"
                logger.info("Got no data as expected")
        
        logger.info("Test passed: get_google_books_data method works correctly")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("process_batch", test_process_batch),
        ("extract_title_from_url", test_extract_title_from_url),
        ("extract_book_id", test_extract_book_id),
        ("get_google_books_data", test_get_google_books_data)
    ]
    
    results = []
    
    for name, test_func in tests:
        logger.info(f"\n{'=' * 50}\nRunning test: {name}\n{'=' * 50}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test {name} failed with exception: {str(e)}")
            results.append((name, False))
    
    # Print summary
    logger.info("\n\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("=" * 50)
    logger.info(f"OVERALL: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    run_all_tests() 