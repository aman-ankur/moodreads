#!/usr/bin/env python3
"""
Test script for the process_batch method flow.

This script tests the actual flow of the process_batch method with minimal inputs,
ensuring that it correctly processes book URLs and updates the database.
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import components
try:
    from moodreads.scraper.goodreads import AdvancedBookScraper
    from moodreads.database.mongodb import MongoDB
except ImportError as e:
    logger.error(f"Error importing components: {str(e)}")
    sys.exit(1)

def test_process_batch_with_single_url():
    """Test process_batch with a single URL."""
    logger.info("Testing process_batch with a single URL...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_process_batch_test"
        db = MongoDB(db_name=db_name)
        
        # Clear existing data for clean test
        db.books_collection.delete_many({})
        
        # Initialize scraper
        scraper = AdvancedBookScraper(db_instance=db)
        
        # Test with a single known book URL
        test_url = "https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye"
        
        # Process the book
        logger.info(f"Processing book: {test_url}")
        scraper.process_batch([test_url], batch_num=1)
        
        # Verify the book was added to the database
        book = db.books_collection.find_one({"url": test_url})
        
        if book:
            logger.info(f"Book successfully added to database: {book.get('title', 'Unknown')}")
            logger.info(f"Book ID: {book.get('_id')}")
            logger.info(f"Book URL: {book.get('url')}")
            logger.info(f"Book author: {book.get('author')}")
            return True
        else:
            logger.error("Book was not added to database")
            return False
        
    except Exception as e:
        logger.error(f"Error in process_batch with single URL: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_process_batch_with_multiple_urls():
    """Test process_batch with multiple URLs."""
    logger.info("Testing process_batch with multiple URLs...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_process_batch_test"
        db = MongoDB(db_name=db_name)
        
        # Clear existing data for clean test
        db.books_collection.delete_many({})
        
        # Initialize scraper
        scraper = AdvancedBookScraper(db_instance=db)
        
        # Test with multiple known book URLs
        test_urls = [
            "https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye",
            "https://www.goodreads.com/book/show/4671.The_Great_Gatsby"
        ]
        
        # Process the books
        logger.info(f"Processing {len(test_urls)} books")
        scraper.process_batch(test_urls, batch_num=1)
        
        # Verify the books were added to the database
        success = True
        for url in test_urls:
            book = db.books_collection.find_one({"url": url})
            
            if book:
                logger.info(f"Book successfully added to database: {book.get('title', 'Unknown')}")
            else:
                logger.error(f"Book was not added to database: {url}")
                success = False
        
        return success
        
    except Exception as e:
        logger.error(f"Error in process_batch with multiple URLs: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_process_batch_with_invalid_url():
    """Test process_batch with an invalid URL."""
    logger.info("Testing process_batch with an invalid URL...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_process_batch_test"
        db = MongoDB(db_name=db_name)
        
        # Initialize scraper
        scraper = AdvancedBookScraper(db_instance=db)
        
        # Test with an invalid URL
        test_url = "https://www.goodreads.com/book/show/invalid_id"
        
        # Process the book
        logger.info(f"Processing book with invalid URL: {test_url}")
        scraper.process_batch([test_url], batch_num=1)
        
        # Verify the book was not added to the database
        book = db.books_collection.find_one({"url": test_url})
        
        if not book:
            logger.info("Invalid URL was correctly handled (not added to database)")
            return True
        else:
            logger.error("Invalid URL was incorrectly added to database")
            return False
        
    except Exception as e:
        # If an exception was raised, check if it was handled properly
        logger.info(f"Exception raised (expected for invalid URL): {str(e)}")
        
        # Check if the exception was handled properly (no book added to database)
        db_name = "moodreads_process_batch_test"
        db = MongoDB(db_name=db_name)
        book = db.books_collection.find_one({"url": "https://www.goodreads.com/book/show/invalid_id"})
        
        if not book:
            logger.info("Invalid URL exception was handled properly (not added to database)")
            return True
        else:
            logger.error("Invalid URL exception was not handled properly (added to database)")
            return False

def main():
    """Main function."""
    try:
        logger.info("Starting process_batch flow tests")
        start_time = time.time()
        
        # Track test results
        results = []
        
        # Run tests
        single_url_success = test_process_batch_with_single_url()
        results.append(("Process Batch with Single URL", single_url_success))
        
        multiple_urls_success = test_process_batch_with_multiple_urls()
        results.append(("Process Batch with Multiple URLs", multiple_urls_success))
        
        invalid_url_success = test_process_batch_with_invalid_url()
        results.append(("Process Batch with Invalid URL", invalid_url_success))
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("PROCESS BATCH FLOW TEST RESULTS")
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
        
        # Print timing
        elapsed_time = time.time() - start_time
        logger.info(f"Total test time: {elapsed_time:.2f} seconds")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        logger.error(f"Error during process_batch flow tests: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 