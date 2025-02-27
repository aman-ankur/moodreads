import argparse
import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Set
import sys
from datetime import datetime
from tqdm import tqdm
import os
import traceback

from moodreads.scraper.goodreads import GoodreadsScraper
from moodreads.database.mongodb import MongoDBClient
from moodreads.analysis.claude import EmotionalAnalyzer

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BookScraper:
    def __init__(self, 
                 batch_size: int = 10,
                 rate_limit: float = 2.0,
                 progress_file: str = "scraping_progress.json"):
        """
        Initialize the book scraper.
        
        Args:
            batch_size: Number of books to process in each batch
            rate_limit: Minimum seconds between requests
            progress_file: File to store scraping progress
        """
        try:
            logger.debug("Starting BookScraper initialization...")
            
            # Clear any proxy settings from environment
            logger.debug("Clearing proxy settings from environment...")
            for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                if proxy_var in os.environ:
                    logger.debug(f"Removing {proxy_var} from environment")
                    os.environ.pop(proxy_var)
            
            # Initialize components with detailed logging
            logger.debug("Initializing GoodreadsScraper...")
            self.scraper = GoodreadsScraper()
            logger.debug("GoodreadsScraper initialized successfully")
            
            logger.debug("Initializing MongoDBClient...")
            self.db = MongoDBClient()
            logger.debug("MongoDBClient initialized successfully")
            
            logger.debug("Initializing EmotionalAnalyzer...")
            self.analyzer = EmotionalAnalyzer()
            logger.debug("EmotionalAnalyzer initialized successfully")
            
            self.batch_size = batch_size
            self.rate_limit = rate_limit
            self.progress_file = Path(progress_file)
            self.processed_urls: Set[str] = set()
            
            logger.debug("Loading progress file...")
            self.load_progress()
            logger.debug("Progress file loaded successfully")
            
            logger.debug("BookScraper initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize BookScraper: {str(e)}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            raise

    def load_progress(self) -> None:
        """Load previously processed URLs from progress file."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                data = json.load(f)
                self.processed_urls = set(data.get("processed_urls", []))
            logger.info(f"Loaded {len(self.processed_urls)} processed URLs")

    def save_progress(self) -> None:
        """Save current progress to file."""
        with open(self.progress_file, 'w') as f:
            json.dump({
                "processed_urls": list(self.processed_urls),
                "last_updated": datetime.now().isoformat()
            }, f)

    def get_category_urls(self, category: str, depth: int) -> List[str]:
        """
        Get book URLs from a Goodreads category page.
        
        Args:
            category: Goodreads category/genre name
            depth: Number of pages to scrape
        
        Returns:
            List of book URLs
        """
        urls = []
        base_url = f"https://www.goodreads.com/shelf/show/{category}"
        
        for page in range(1, depth + 1):
            try:
                page_urls = self.scraper.get_book_urls_from_page(f"{base_url}?page={page}")
                urls.extend(page_urls)
                time.sleep(self.rate_limit)
            except Exception as e:
                logger.error(f"Error scraping category page {page}: {str(e)}")
        
        return list(set(urls))  # Remove duplicates

    def process_batch(self, urls: List[str]) -> None:
        """Process a batch of book URLs."""
        for url in urls:
            if url in self.processed_urls:
                continue
                
            try:
                # Scrape book data
                book_data = self.scraper.scrape_book(url)
                if not book_data:
                    continue
                
                # Generate emotional profile and embedding
                emotional_profile, embedding = self.analyzer.analyze_book(
                    book_data['description'],
                    book_data.get('reviews', []),
                    book_data.get('genres', [])
                )
                
                # Add to database
                book_data['emotional_profile'] = emotional_profile
                book_data['embedding'] = embedding.tolist()
                book_data['scraped_at'] = datetime.now()
                
                self.db.add_book(book_data)
                self.processed_urls.add(url)
                
                # Respect rate limits
                time.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
            
            # Save progress after each book
            self.save_progress()

    def scrape_books(self, categories: List[str], depth: int) -> None:
        """
        Main scraping function.
        
        Args:
            categories: List of Goodreads categories to scrape
            depth: Number of pages to scrape per category
        """
        for category in categories:
            logger.info(f"Processing category: {category}")
            
            # Get book URLs for category
            urls = self.get_category_urls(category, depth)
            new_urls = [url for url in urls if url not in self.processed_urls]
            
            if not new_urls:
                logger.info(f"No new books found in category {category}")
                continue
            
            # Process in batches with progress bar
            batches = [new_urls[i:i + self.batch_size] 
                      for i in range(0, len(new_urls), self.batch_size)]
            
            with tqdm(total=len(batches), desc=f"Processing {category}") as pbar:
                for batch in batches:
                    self.process_batch(batch)
                    pbar.update(1)
            
            logger.info(f"Completed category: {category}")

def main():
    parser = argparse.ArgumentParser(description="Scrape books from Goodreads")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["fiction", "mystery", "science-fiction", "romance", "fantasy"],
        help="Goodreads categories to scrape"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="Number of pages to scrape per category"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of books to process in each batch"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=3.0,
        help="Minimum seconds between requests"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper with explicit error handling
        try:
            scraper = BookScraper(
                batch_size=args.batch_size,
                rate_limit=args.rate_limit
            )
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {str(e)}")
            raise
            
        # Start scraping with explicit error handling
        try:
            scraper.scrape_books(args.categories, args.depth)
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        if 'scraper' in locals():
            scraper.save_progress()
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        # Print full traceback for debugging
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 