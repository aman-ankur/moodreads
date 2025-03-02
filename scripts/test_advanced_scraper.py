#!/usr/bin/env python3
"""
Test script for the advanced book scraper.
This script will scrape a small number of books from a single category
to verify that the advanced scraper is working correctly.
"""

import argparse
import logging
import sys
import os
import json
import time
import signal
import atexit
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the advanced scraper
from scripts.scrape_books import AdvancedBookScraper
from moodreads.analysis.vector_embeddings import VectorEmbeddingStore

# Global reference to the vector embedding store
vector_store = None

def save_mappings_on_exit():
    """Save emotion mappings when the script exits."""
    global vector_store
    if vector_store:
        logger.info("Saving emotion mappings before exit...")
        vector_store.save_mappings()
        logger.info("Emotion mappings saved.")

def signal_handler(sig, frame):
    """Handle signals like CTRL+C to ensure clean exit."""
    logger.info(f"Received signal {sig}, exiting gracefully...")
    save_mappings_on_exit()
    sys.exit(0)

def test_scraper(category, num_books, db_name, timeout=300, skip_analysis=False):
    """
    Test the advanced scraper with a small number of books.
    
    Args:
        category: Goodreads category to scrape
        num_books: Maximum number of books to scrape
        db_name: MongoDB database name to use
        timeout: Maximum time in seconds to allow for processing a single book
        skip_analysis: Whether to skip emotional analysis (faster testing)
    """
    global vector_store
    
    try:
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        logger.info(f"Testing advanced scraper with category: {category}, num_books: {num_books}, db_name: {db_name}")
        logger.info(f"Timeout: {timeout}s, Skip analysis: {skip_analysis}")
        
        # Initialize the vector embedding store for emotion mappings
        vector_store = VectorEmbeddingStore()
        
        # Register exit handlers to save mappings
        atexit.register(save_mappings_on_exit)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize the scraper with skip_analysis option
        scraper = AdvancedBookScraper(
            batch_size=1,  # Process one book at a time for testing
            rate_limit=3.0,  # Be gentle with the API
            db_name=db_name,
            progress_file=f"test_scraping_progress_{category}.json",  # Use a separate progress file for testing
            skip_emotional_analysis=skip_analysis  # Skip emotional analysis if requested
        )
        
        # Get book URLs for the category (just the first page)
        logger.info(f"Getting book URLs for category: {category}")
        urls = scraper.get_category_urls(category, depth=1)
        
        # Limit to the specified number of books
        urls = urls[:num_books]
        logger.info(f"Found {len(urls)} URLs, processing up to {num_books}")
        
        # Process each book with timeout
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing book {i}/{len(urls)}: {url}")
            
            # Set a timeout for processing this book
            start_time = time.time()
            try:
                scraper.process_batch([url], batch_num=i)
                
                # Check if we've exceeded the timeout
                elapsed_time = time.time() - start_time
                logger.info(f"Processed book in {elapsed_time:.2f} seconds")
                
                if elapsed_time > timeout:
                    logger.warning(f"Processing took longer than expected ({elapsed_time:.2f}s > {timeout}s)")
            
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"Error processing book after {elapsed_time:.2f}s: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Continue with next book
                logger.info("Continuing with next book...")
                continue
        
        logger.info("Test completed successfully")
        
        # Save mappings at the end
        save_mappings_on_exit()
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Test the advanced book scraper")
    parser.add_argument(
        "--category",
        type=str,
        default="science-fiction",
        help="Goodreads category to scrape"
    )
    parser.add_argument(
        "--num-books",
        type=int,
        default=3,
        help="Maximum number of books to scrape"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="moodreads_advanced_test",
        help="MongoDB database name to use"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum time in seconds to allow for processing a single book"
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip emotional analysis (faster testing)"
    )
    
    args = parser.parse_args()
    
    test_scraper(args.category, args.num_books, args.db_name, args.timeout, args.skip_analysis)

if __name__ == "__main__":
    main() 