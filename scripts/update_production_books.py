#!/usr/bin/env python3
"""
Production book scraper script.
This script will scrape books from multiple categories and update them
with the latest emotional analysis and vector embeddings.
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
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/production_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
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

def process_categories(categories: List[str], books_per_category: int, db_name: str, timeout: int = 300):
    """
    Process multiple categories of books for the production database.
    
    Args:
        categories: List of Goodreads categories to scrape
        books_per_category: Number of books to process per category
        db_name: MongoDB database name to use
        timeout: Maximum time in seconds to allow for processing a single book
    """
    global vector_store
    
    try:
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        logger.info(f"Starting production scraper with {len(categories)} categories")
        logger.info(f"Categories: {', '.join(categories)}")
        logger.info(f"Books per category: {books_per_category}")
        logger.info(f"Database: {db_name}")
        
        # Initialize the vector embedding store for emotion mappings
        vector_store = VectorEmbeddingStore()
        
        # Register exit handlers to save mappings
        atexit.register(save_mappings_on_exit)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        total_processed = 0
        total_errors = 0
        
        for category in categories:
            logger.info(f"Processing category: {category}")
            
            # Initialize the scraper for this category
            scraper = AdvancedBookScraper(
                batch_size=1,  # Process one book at a time for better control
                rate_limit=3.0,  # Be gentle with the API
                db_name=db_name,
                progress_file=f"production_scraping_progress_{category}.json",
                skip_emotional_analysis=False  # Always perform emotional analysis in production
            )
            
            # Get book URLs for the category
            logger.info(f"Getting book URLs for category: {category}")
            urls = scraper.get_category_urls(category, depth=2)  # Get more books to choose from
            
            # Limit to the specified number of books
            urls = urls[:books_per_category]
            logger.info(f"Found {len(urls)} URLs, processing up to {books_per_category}")
            
            category_processed = 0
            category_errors = 0
            
            # Process each book with timeout
            for i, url in enumerate(urls, 1):
                logger.info(f"Processing book {i}/{len(urls)} from {category}: {url}")
                
                # Set a timeout for processing this book
                start_time = time.time()
                try:
                    scraper.process_batch([url], batch_num=i)
                    
                    # Check if we've exceeded the timeout
                    elapsed_time = time.time() - start_time
                    logger.info(f"Processed book in {elapsed_time:.2f} seconds")
                    
                    if elapsed_time > timeout:
                        logger.warning(f"Processing took longer than expected ({elapsed_time:.2f}s > {timeout}s)")
                    
                    category_processed += 1
                    total_processed += 1
                
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    logger.error(f"Error processing book after {elapsed_time:.2f}s: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    category_errors += 1
                    total_errors += 1
                    
                    # Continue with next book
                    logger.info("Continuing with next book...")
                    continue
            
            logger.info(f"Completed category {category}: {category_processed} books processed, {category_errors} errors")
        
        logger.info(f"All categories completed: {total_processed} total books processed, {total_errors} total errors")
        
        # Save mappings at the end
        save_mappings_on_exit()
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Process books for production database with advanced emotional analysis")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["fiction", "science-fiction", "fantasy", "mystery", "romance"],
        help="Goodreads categories to scrape (space-separated list)"
    )
    parser.add_argument(
        "--books-per-category",
        type=int,
        default=10,
        help="Number of books to process per category"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="moodreads_production",
        help="MongoDB database name to use"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum time in seconds to allow for processing a single book"
    )
    
    args = parser.parse_args()
    
    process_categories(args.categories, args.books_per_category, args.db_name, args.timeout)

if __name__ == "__main__":
    main() 