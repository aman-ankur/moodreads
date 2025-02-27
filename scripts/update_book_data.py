import os
import sys
from pymongo import MongoClient
from tqdm import tqdm
import time
import logging
from src.moodreads.scraper.goodreads import GoodreadsScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('update_books.log')
    ]
)
logger = logging.getLogger(__name__)

def get_mongodb_uri():
    """Get MongoDB URI from environment variable."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI environment variable not set")
    return uri

def update_books():
    """Update all book entries with fresh data from Goodreads."""
    try:
        # Connect to MongoDB
        client = MongoClient(get_mongodb_uri())
        db = client.get_default_database()
        books_collection = db.books
        
        # Get all existing books
        existing_books = list(books_collection.find({}, {"url": 1, "_id": 1}))
        logger.info(f"Found {len(existing_books)} books to update")
        
        # Initialize scraper
        scraper = GoodreadsScraper()
        
        # Update each book
        updated_count = 0
        error_count = 0
        
        for book in tqdm(existing_books, desc="Updating books"):
            try:
                # Skip if no URL (shouldn't happen, but just in case)
                if not book.get("url"):
                    logger.warning(f"Book {book['_id']} has no URL, skipping")
                    continue
                
                # Scrape fresh data
                fresh_data = scraper.scrape_book(book["url"])
                
                if fresh_data:
                    # Update the book entry
                    result = books_collection.update_one(
                        {"_id": book["_id"]},
                        {"$set": fresh_data}
                    )
                    
                    if result.modified_count > 0:
                        updated_count += 1
                        logger.debug(f"Updated book: {fresh_data['title']}")
                    else:
                        logger.warning(f"No changes for book: {fresh_data['title']}")
                
                # Sleep to respect rate limits
                time.sleep(2)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error updating book {book['_id']}: {str(e)}")
                continue
        
        logger.info(f"Update complete. Updated {updated_count} books. Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    update_books() 