import argparse
import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Set, Any, Optional
import sys
from datetime import datetime
from tqdm import tqdm
import os
import traceback
import requests
import re
from urllib.parse import quote_plus

from moodreads.scraper.goodreads import GoodreadsScraper
from moodreads.database.mongodb import MongoDBClient
from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.analysis.vector_embeddings import VectorEmbeddingStore
from decouple import config

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AdvancedBookScraper:
    def __init__(self, 
                 batch_size: int = 10,
                 rate_limit: float = 2.0,
                 progress_file: str = "scraping_progress.json",
                 db_name: str = "moodreads_advanced",
                 skip_emotional_analysis: bool = False):
        """
        Initialize the advanced book scraper.
        
        Args:
            batch_size: Number of books to process in each batch
            rate_limit: Minimum seconds between requests
            progress_file: File to store scraping progress
            db_name: Name of the MongoDB database to use
            skip_emotional_analysis: Whether to skip emotional analysis (faster testing)
        """
        try:
            logger.debug("Starting AdvancedBookScraper initialization...")
            
            # Clear any proxy settings from environment
            logger.debug("Clearing proxy settings from environment...")
            for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                if proxy_var in os.environ:
                    logger.debug(f"Removing {proxy_var} from environment")
                    os.environ.pop(proxy_var)
            
            # Set environment variable for MongoDB database name
            os.environ['MONGODB_DB_NAME'] = db_name
            logger.debug(f"Set MongoDB database name to: {db_name}")
            
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
            
            logger.debug("Initializing VectorEmbeddingStore...")
            self.vector_store = VectorEmbeddingStore()
            logger.debug("VectorEmbeddingStore initialized successfully")
            
            # Get Google Books API key
            self.google_api_key = config('GOOGLE_BOOKS_API_KEY', default=config('GOOGLE_API_KEY', default=None))
            if not self.google_api_key:
                logger.warning("Google Books API key not found in environment variables")
            else:
                logger.debug("Google Books API key loaded successfully")
            
            self.batch_size = batch_size
            self.rate_limit = rate_limit
            self.progress_file = Path(progress_file)
            self.processed_urls: Set[str] = set()
            self.skip_emotional_analysis = skip_emotional_analysis
            
            if self.skip_emotional_analysis:
                logger.info("Emotional analysis will be skipped (testing mode)")
            
            logger.debug("Loading progress file...")
            self.load_progress()
            logger.debug("Progress file loaded successfully")
            
            # Create logs directory if it doesn't exist
            Path("logs").mkdir(exist_ok=True)
            
            logger.debug("AdvancedBookScraper initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AdvancedBookScraper: {str(e)}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            raise

    def load_progress(self) -> None:
        """Load previously processed URLs from progress file."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                data = json.load(f)
                self.processed_urls = set(data.get("processed_urls", []))
            logger.info(f"Loaded {len(self.processed_urls)} processed URLs")
        else:
            logger.info("No progress file found, starting fresh")

    def save_progress(self) -> None:
        """Save current progress to file."""
        with open(self.progress_file, 'w') as f:
            json.dump({
                "processed_urls": list(self.processed_urls),
                "last_updated": datetime.now().isoformat()
            }, f)
        logger.debug(f"Progress saved: {len(self.processed_urls)} URLs processed")

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
                logger.debug(f"Scraping category page {page} for {category}")
                page_urls = self.scraper.get_book_urls_from_page(f"{base_url}?page={page}")
                urls.extend(page_urls)
                logger.debug(f"Found {len(page_urls)} books on page {page}")
                time.sleep(self.rate_limit)
            except Exception as e:
                logger.error(f"Error scraping category page {page}: {str(e)}")
        
        unique_urls = list(set(urls))  # Remove duplicates
        logger.info(f"Found {len(unique_urls)} unique book URLs for category {category}")
        return unique_urls

    def get_google_books_data(self, title: str, author: str, isbn: Optional[str] = None) -> Dict[str, Any]:
        """
        Get book data from Google Books API.
        
        Args:
            title: Book title
            author: Book author
            isbn: ISBN (optional)
            
        Returns:
            Dictionary with Google Books data
        """
        if not title and not author and not isbn:
            logger.warning("Cannot query Google Books API without title, author, or ISBN")
            return {}
            
        try:
            # Build query
            query_parts = []
            
            if isbn:
                query_parts.append(f"isbn:{isbn}")
            
            if title:
                # Clean title - remove series information in parentheses
                clean_title = re.sub(r'\s*\(.*?\)\s*', ' ', title).strip()
                query_parts.append(f"intitle:{clean_title}")
            
            if author:
                query_parts.append(f"inauthor:{author}")
            
            query = " ".join(query_parts)
            
            if not query:
                logger.warning("Empty query for Google Books API")
                return {}
                
            logger.debug(f"Querying Google Books API: {query}")
            
            # Make API request
            api_key = os.environ.get('GOOGLE_BOOKS_API_KEY') or os.environ.get('GOOGLE_API_KEY')
            url = f"https://www.googleapis.com/books/v1/volumes?q={quote_plus(query)}"
            
            if api_key:
                url += f"&key={api_key}"
                
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' not in data or not data['items']:
                logger.warning(f"No results found in Google Books API for: {title} by {author}")
                return {}
            
            # Get the first item
            item = data['items'][0]
            volume_info = item.get('volumeInfo', {})
            
            # Extract relevant data
            google_data = {
                'google_id': item.get('id'),
                'google_self_link': item.get('selfLink'),
                'google_description': volume_info.get('description', ''),
                'google_categories': volume_info.get('categories', []),
                'google_page_count': volume_info.get('pageCount'),
                'google_published_date': volume_info.get('publishedDate'),
                'google_publisher': volume_info.get('publisher', ''),
                'google_rating': volume_info.get('averageRating'),
                'google_rating_count': volume_info.get('ratingsCount'),
                'google_language': volume_info.get('language'),
                'google_preview_link': volume_info.get('previewLink'),
                'google_info_link': volume_info.get('infoLink')
            }
            
            # Get thumbnail
            if 'imageLinks' in volume_info:
                image_links = volume_info['imageLinks']
                # Try to get the largest available image
                for img_type in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
                    if img_type in image_links:
                        google_data['google_thumbnail'] = image_links[img_type]
                        break
            
            # Get identifiers
            if 'industryIdentifiers' in volume_info:
                for identifier in volume_info['industryIdentifiers']:
                    id_type = identifier.get('type', '')
                    id_value = identifier.get('identifier', '')
                    
                    if id_type == 'ISBN_10':
                        google_data['google_isbn'] = id_value
                    elif id_type == 'ISBN_13':
                        google_data['google_isbn13'] = id_value
            
            logger.debug(f"Successfully retrieved Google Books data for {title} by {author}")
            return google_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying Google Books API: {str(e)}")
            return {}
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Google Books API response: {str(e)}")
            return {}

    def scrape_basic_book_data(self, url: str, skip_reviews: bool = False) -> Dict[str, Any]:
        """
        Scrape only the essential book data from Goodreads without quotes.
        
        Args:
            url: Goodreads book URL
            skip_reviews: Whether to skip fetching reviews (faster testing)
            
        Returns:
            Dictionary with basic book data
        """
        try:
            logger.debug(f"Scraping basic book data from: {url}")
            
            # Use the existing scraper but tell it to skip quotes
            book_data = self.scraper.scrape_book(url, skip_quotes=True)
            
            if not book_data:
                logger.warning(f"No book data found for URL: {url}")
                return {}
            
            # Validate essential data
            title = book_data.get('title')
            author = book_data.get('author')
            
            if not title:
                logger.warning(f"No title found for book: {url}")
                # Try to extract from URL as fallback
                title_from_url = url.split('/')[-1].split('.')[-1].replace('-', ' ').title()
                book_data['title'] = title_from_url
                title = title_from_url
                logger.debug(f"Using title from URL: {title}")
            
            if not author:
                logger.warning(f"No author found for book: {title} ({url})")
            
            logger.debug(f"Successfully scraped basic data for: {title} by {author or 'Unknown author'}")
            return book_data
            
        except Exception as e:
            logger.error(f"Error scraping basic book data from {url}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}

    def process_batch(self, batch: List[str], batch_num: int) -> None:
        """
        Process a batch of book URLs.
        
        Args:
            batch: List of book URLs
            batch_num: Batch number
        """
        logger.info(f"Processing batch {batch_num} with {len(batch)} URLs")
        
        for url in batch:
            try:
                # Skip if already processed
                if url in self.processed_urls:
                    logger.info(f"Skipping already processed URL: {url}")
                    continue
                
                # Extract book ID from URL
                book_id = self._extract_book_id(url)
                if not book_id:
                    logger.warning(f"Could not extract book ID from URL: {url}")
                    self.processed_urls.add(url)
                    continue
                
                # Check if book already exists in database
                existing_book = self.db.books_collection.find_one({"goodreads_id": book_id})
                if existing_book:
                    logger.info(f"Book already exists in database: {book_id}")
                    self.processed_urls.add(url)
                    continue
                
                # Scrape basic book data
                start_time = time.time()
                book_data = self.scrape_basic_book_data(url, skip_reviews=self.skip_emotional_analysis)
                
                if not book_data:
                    logger.warning(f"Failed to scrape book data for URL: {url}")
                    self.processed_urls.add(url)
                    continue
                
                # Validate essential book data
                title = book_data.get('title', '')
                author = book_data.get('author', '')
                
                if not title or title == 'Unknown':
                    # Try to extract title from URL
                    title_from_url = self._extract_title_from_url(url)
                    if title_from_url:
                        logger.info(f"Using title from URL: {title_from_url}")
                        book_data['title'] = title_from_url
                        title = title_from_url
                    else:
                        logger.warning(f"Missing title for book: {url}")
                
                if not author or author == 'Unknown':
                    logger.warning(f"Missing author for book: {title} - {url}")
                
                logger.debug(f"Scraped book: {title} by {author}")
                
                # Get Google Books data
                if title and author:
                    try:
                        google_data = self.get_google_books_data(title, author, book_data.get('isbn', ''))
                        if google_data:
                            book_data.update(google_data)
                    except Exception as e:
                        logger.error(f"Error getting Google Books data: {e}")
                
                # Add source and timestamp
                book_data['source'] = 'advanced_scraper'
                book_data['scraped_at'] = datetime.now().isoformat()
                
                # Skip emotional analysis if requested
                if not self.skip_emotional_analysis:
                    # Get enhanced reviews
                    if not book_data.get('reviews_data'):
                        logger.info(f"Getting enhanced reviews for: {title}")
                        reviews = self.scraper.get_enhanced_reviews(url)
                        book_data['reviews_data'] = reviews
                    
                    # Perform emotional analysis
                    try:
                        logger.info(f"Performing emotional analysis for: {title}")
                        emotional_profile = self.analyzer.analyze_book_enhanced(
                            description=book_data.get('description', ''),
                            reviews=book_data.get('reviews_data', []),
                            genres=book_data.get('genres', []),
                            book_id=book_id
                        )
                        
                        # Ensure emotional_profile has the correct structure
                        if isinstance(emotional_profile, list):
                            # Convert list to dictionary format
                            book_data['emotional_profile'] = {
                                'primary_emotions': emotional_profile
                            }
                        else:
                            book_data['emotional_profile'] = emotional_profile
                        
                        # Generate vector embedding
                        logger.debug(f"Generating vector embedding for: {title}")
                        vector = self.vector_store.generate_emotion_vector(book_data['emotional_profile'])
                        book_data['emotional_profile']['embedding'] = vector.tolist()
                        
                        # Copy the embedding to the top-level field for efficient similarity searches
                        book_data['embedding'] = vector.tolist()
                        
                    except Exception as e:
                        logger.error(f"Error during emotional analysis: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        book_data['emotional_analysis_error'] = str(e)
                        # Add placeholder data
                        book_data['emotional_profile'] = {
                            'primary_emotions': [{'emotion': 'test', 'intensity': 5}]
                        }
                        # Use the correct length for the placeholder embedding
                        embedding_length = len(self.analyzer.primary_emotions)
                        book_data['emotional_profile']['embedding'] = [0.0] * embedding_length
                        book_data['embedding'] = [0.0] * embedding_length
                        book_data['skip_emotional_analysis'] = True
                else:
                    # Add placeholder data for testing
                    logger.info(f"Skipping emotional analysis for: {title}")
                    book_data['emotional_profile'] = {
                        'primary_emotions': [{'emotion': 'test', 'intensity': 5}]
                    }
                    # Use the correct length for the placeholder embedding
                    embedding_length = len(self.analyzer.primary_emotions)
                    book_data['emotional_profile']['embedding'] = [0.0] * embedding_length
                    book_data['embedding'] = [0.0] * embedding_length
                    book_data['skip_emotional_analysis'] = True
                
                # Add book to database
                logger.debug(f"Adding book to database: {title} by {author}")
                result = self.db.add_book(book_data)
                
                if result:
                    logger.info(f"Successfully processed book: {title} by {author}")
                else:
                    logger.warning(f"Failed to add book to database: {title}")
                
                # Add URL to processed URLs
                self.processed_urls.add(url)
                
                # Save progress
                self._save_progress()
                
                # Sleep to avoid rate limiting
                time.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                self.processed_urls.add(url)
                continue

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
            
            logger.info(f"Found {len(new_urls)} new books to process in category {category}")
            
            # Process in batches with progress bar
            batches = [new_urls[i:i + self.batch_size] 
                      for i in range(0, len(new_urls), self.batch_size)]
            
            with tqdm(total=len(batches), desc=f"Processing {category}") as pbar:
                for batch_num, batch in enumerate(batches):
                    self.process_batch(batch, batch_num + 1)
                    pbar.update(1)
            
            logger.info(f"Completed category: {category}")

    def _extract_book_id(self, url: str) -> str:
        """
        Extract book ID from URL.
        
        Args:
            url: Book URL
            
        Returns:
            Book ID
        """
        # Extract book ID from URL (e.g., https://www.goodreads.com/book/show/70535.2001)
        match = re.search(r'/show/(\d+)', url)
        if match:
            return match.group(1)
        return ""

    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract title from URL as a fallback.
        
        Args:
            url: Book URL
            
        Returns:
            Book title
        """
        # Extract title from URL (e.g., https://www.goodreads.com/book/show/70535.2001)
        # or https://www.goodreads.com/book/show/21611.The_Forever_War
        match = re.search(r'/show/\d+\.([^/]+)', url)
        if match:
            title = match.group(1)
            # Clean up the title
            title = title.replace('_', ' ').replace('-', ' ')
            # Convert to title case
            title = ' '.join(word.capitalize() for word in title.split())
            return title
        return ""

    def _save_progress(self) -> None:
        """
        Save progress to file.
        """
        # Save processed URLs to file
        with open(self.progress_file, 'w') as f:
            json.dump({
                'processed_urls': list(self.processed_urls),
                'timestamp': datetime.now().isoformat()
            }, f)
        
        logger.debug(f"Progress saved: {len(self.processed_urls)} URLs processed")

def main():
    parser = argparse.ArgumentParser(description="Scrape books from Goodreads with advanced emotional analysis")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["fiction", "mystery", "science-fiction", "romance", "fantasy", "thriller", "historical-fiction", "non-fiction", "young-adult", "horror"],
        help="Goodreads categories to scrape"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Number of pages to scrape per category"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of books to process in each batch"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=3.0,
        help="Minimum seconds between requests"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="moodreads_advanced",
        help="MongoDB database name to use"
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip emotional analysis (faster testing)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper with explicit error handling
        try:
            scraper = AdvancedBookScraper(
                batch_size=args.batch_size,
                rate_limit=args.rate_limit,
                db_name=args.db_name,
                skip_emotional_analysis=args.skip_analysis
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