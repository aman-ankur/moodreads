#!/usr/bin/env python3
"""
Enhanced Goodreads Scraper
Collects detailed book information from Goodreads including reviews, quotes, and additional metadata.
"""

import requests
import time
import logging
import random
import re
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedGoodreadsScraper:
    """Enhanced scraper for Goodreads that collects detailed book information."""
    
    BASE_URL = "https://www.goodreads.com"
    SEARCH_URL = f"{BASE_URL}/search?q="
    
    # User agents to rotate for avoiding detection
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    ]
    
    def __init__(self, delay_between_requests: float = 2.0, max_retries: int = 3):
        """
        Initialize the scraper.
        
        Args:
            delay_between_requests: Delay between requests in seconds to avoid rate limiting
            max_retries: Maximum number of retries for failed requests
        """
        self.delay = delay_between_requests
        self.max_retries = max_retries
        self.session = requests.Session()
        self._rotate_user_agent()
        logger.info("Enhanced Goodreads scraper initialized")
    
    def _rotate_user_agent(self) -> None:
        """Rotate user agent to avoid detection."""
        user_agent = random.choice(self.USER_AGENTS)
        self.session.headers.update({"User-Agent": user_agent})
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a request to the given URL with retries and delay.
        
        Args:
            url: URL to request
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        for attempt in range(self.max_retries):
            try:
                # Rotate user agent for each attempt
                self._rotate_user_agent()
                
                # Add jitter to delay to make requests look more human
                jitter = random.uniform(-0.5, 0.5)
                time.sleep(max(0.5, self.delay + jitter))
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                return BeautifulSoup(response.text, "html.parser")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to retrieve {url} after {self.max_retries} attempts")
                    return None
        
        return None
    
    def search_books(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for books on Goodreads.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of book dictionaries with basic information
        """
        logger.info(f"Searching for books with query: {query}")
        
        search_url = f"{self.SEARCH_URL}{quote_plus(query)}"
        soup = self._make_request(search_url)
        
        if not soup:
            logger.error("Failed to retrieve search results")
            return []
        
        results = []
        book_elements = soup.select("tr[itemtype='http://schema.org/Book']")
        
        for i, book_element in enumerate(book_elements[:max_results]):
            try:
                # Extract book information
                title_element = book_element.select_one(".bookTitle span")
                author_element = book_element.select_one(".authorName span")
                rating_element = book_element.select_one(".minirating")
                cover_element = book_element.select_one("img.bookCover")
                link_element = book_element.select_one(".bookTitle")
                
                if not title_element or not link_element:
                    continue
                
                title = title_element.text.strip()
                author = author_element.text.strip() if author_element else "Unknown"
                goodreads_url = f"{self.BASE_URL}{link_element['href']}" if link_element.has_attr('href') else None
                
                # Extract rating and ratings count
                rating_text = rating_element.text.strip() if rating_element else ""
                avg_rating = None
                ratings_count = None
                
                if rating_text:
                    rating_match = re.search(r"(\d+\.\d+)", rating_text)
                    count_match = re.search(r"(\d+(?:,\d+)*)\s+ratings", rating_text)
                    
                    if rating_match:
                        avg_rating = float(rating_match.group(1))
                    
                    if count_match:
                        ratings_count = int(count_match.group(1).replace(",", ""))
                
                # Extract cover URL
                cover_url = cover_element["src"] if cover_element and cover_element.has_attr("src") else None
                
                # Create book dictionary
                book = {
                    "title": title,
                    "author": author,
                    "goodreads_url": goodreads_url,
                    "avg_rating": avg_rating,
                    "ratings_count": ratings_count,
                    "cover_url": cover_url
                }
                
                results.append(book)
                logger.debug(f"Found book: {title} by {author}")
                
            except Exception as e:
                logger.warning(f"Error extracting book information: {e}")
                continue
        
        logger.info(f"Found {len(results)} books for query: {query}")
        return results
    
    def get_book_details(self, goodreads_url: str) -> Optional[Dict]:
        """
        Get detailed information about a book from its Goodreads URL.
        
        Args:
            goodreads_url: URL of the book on Goodreads
            
        Returns:
            Dictionary with detailed book information or None if retrieval failed
        """
        logger.info(f"Getting detailed information for book: {goodreads_url}")
        
        soup = self._make_request(goodreads_url)
        
        if not soup:
            logger.error(f"Failed to retrieve book details from {goodreads_url}")
            return None
        
        try:
            # Extract basic information
            title_element = soup.select_one("h1#bookTitle")
            author_element = soup.select_one("a.authorName span")
            description_element = soup.select_one("#description span[style='display:none']") or soup.select_one("#description span")
            isbn_element = soup.select_one("meta[property='books:isbn']")
            
            title = title_element.text.strip() if title_element else "Unknown Title"
            author = author_element.text.strip() if author_element else "Unknown Author"
            description = description_element.text.strip() if description_element else ""
            isbn = isbn_element["content"] if isbn_element and isbn_element.has_attr("content") else None
            
            # Extract rating information
            rating_element = soup.select_one("div.ratingValue span[itemprop='ratingValue']")
            ratings_count_element = soup.select_one("meta[itemprop='ratingCount']")
            
            avg_rating = float(rating_element.text.strip()) if rating_element else None
            ratings_count = int(ratings_count_element["content"]) if ratings_count_element and ratings_count_element.has_attr("content") else None
            
            # Extract genres/shelves
            genres = []
            genre_elements = soup.select("div.elementList div.left a.actionLinkLite.bookPageGenreLink")
            
            for genre_element in genre_elements:
                genre = genre_element.text.strip()
                if genre:
                    genres.append(genre)
            
            # Extract publication information
            published_element = soup.select_one("#details span[itemprop='publicationEdition']")
            published_date = None
            
            if published_element:
                published_text = published_element.text.strip()
                date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+(?:st|nd|rd|th)?\s+\d{4}", published_text)
                
                if date_match:
                    published_date = date_match.group(0)
            
            # Extract page count
            pages_element = soup.select_one("span[itemprop='numberOfPages']")
            page_count = None
            
            if pages_element:
                pages_text = pages_element.text.strip()
                pages_match = re.search(r"(\d+)", pages_text)
                
                if pages_match:
                    page_count = int(pages_match.group(1))
            
            # Extract cover URL
            cover_element = soup.select_one("#coverImage")
            cover_url = cover_element["src"] if cover_element and cover_element.has_attr("src") else None
            
            # Extract quotes
            quotes = self._extract_quotes(soup)
            
            # Create book dictionary
            book = {
                "title": title,
                "author": author,
                "description": description,
                "isbn": isbn,
                "avg_rating": avg_rating,
                "ratings_count": ratings_count,
                "genres": genres,
                "published_date": published_date,
                "page_count": page_count,
                "cover_url": cover_url,
                "goodreads_url": goodreads_url,
                "quotes": quotes
            }
            
            logger.info(f"Successfully retrieved details for book: {title} by {author}")
            return book
            
        except Exception as e:
            logger.error(f"Error extracting book details: {e}")
            return None
    
    def _extract_quotes(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract quotes from the book page.
        
        Args:
            soup: BeautifulSoup object of the book page
            
        Returns:
            List of quotes
        """
        quotes = []
        quote_elements = soup.select("div.quoteText")
        
        for quote_element in quote_elements[:5]:  # Limit to 5 quotes
            quote_text = quote_element.get_text(strip=True)
            # Remove attribution part (usually after em dash or quotes)
            quote_text = re.split(r"―|\"", quote_text)[0].strip()
            if quote_text:
                quotes.append(quote_text)
        
        return quotes
    
    def get_book_reviews(self, goodreads_url: str, max_reviews: int = 10, min_text_length: int = 100) -> List[Dict]:
        """
        Get reviews for a book from its Goodreads URL.
        
        Args:
            goodreads_url: URL of the book on Goodreads
            max_reviews: Maximum number of reviews to retrieve
            min_text_length: Minimum length of review text to include
            
        Returns:
            List of review dictionaries
        """
        logger.info(f"Getting reviews for book: {goodreads_url}")
        
        # Construct reviews URL
        book_id_match = re.search(r"/show/(\d+)", goodreads_url)
        if not book_id_match:
            logger.error(f"Could not extract book ID from URL: {goodreads_url}")
            return []
        
        book_id = book_id_match.group(1)
        reviews_url = f"{self.BASE_URL}/book/reviews/{book_id}?sort=newest"
        
        soup = self._make_request(reviews_url)
        
        if not soup:
            logger.error(f"Failed to retrieve reviews from {reviews_url}")
            return []
        
        reviews = []
        review_elements = soup.select("div.review")
        
        for review_element in review_elements:
            try:
                # Extract reviewer information
                reviewer_element = review_element.select_one("a.user")
                reviewer = reviewer_element.text.strip() if reviewer_element else "Anonymous"
                
                # Extract rating
                rating_element = review_element.select_one("span.staticStars")
                rating = None
                
                if rating_element:
                    rating_class = rating_element.get("class", [])
                    rating_match = next((re.search(r"p(\d+)", c) for c in rating_class if re.search(r"p(\d+)", c)), None)
                    
                    if rating_match:
                        rating = int(rating_match.group(1)) / 10  # Convert from 0-50 scale to 0-5
                
                # Extract review text
                text_element = review_element.select_one("div.reviewText span[style='display:none']") or review_element.select_one("div.reviewText span")
                text = text_element.text.strip() if text_element else ""
                
                # Skip reviews that are too short
                if len(text) < min_text_length:
                    continue
                
                # Extract date
                date_element = review_element.select_one("a.reviewDate")
                date = date_element.text.strip() if date_element else None
                
                # Extract likes
                likes_element = review_element.select_one("span.likesCount")
                likes = 0
                
                if likes_element:
                    likes_match = re.search(r"(\d+)", likes_element.text)
                    
                    if likes_match:
                        likes = int(likes_match.group(1))
                
                # Create review dictionary
                review = {
                    "reviewer": reviewer,
                    "rating": rating,
                    "text": text,
                    "date": date,
                    "likes": likes
                }
                
                reviews.append(review)
                
                # Stop if we have enough reviews
                if len(reviews) >= max_reviews:
                    break
                    
            except Exception as e:
                logger.warning(f"Error extracting review: {e}")
                continue
        
        logger.info(f"Retrieved {len(reviews)} reviews for book")
        return reviews
    
    def process_book(self, query: str) -> Optional[Dict]:
        """
        Process a book by searching for it and retrieving detailed information and reviews.
        
        Args:
            query: Search query for the book
            
        Returns:
            Dictionary with complete book information or None if processing failed
        """
        logger.info(f"Processing book: {query}")
        
        # Search for the book
        search_results = self.search_books(query, max_results=1)
        
        if not search_results:
            logger.error(f"No books found for query: {query}")
            return None
        
        book = search_results[0]
        goodreads_url = book.get("goodreads_url")
        
        if not goodreads_url:
            logger.error(f"No Goodreads URL found for book: {book['title']}")
            return None
        
        # Get detailed information
        book_details = self.get_book_details(goodreads_url)
        
        if not book_details:
            logger.error(f"Failed to retrieve details for book: {book['title']}")
            return None
        
        # Get reviews
        reviews = self.get_book_reviews(goodreads_url)
        book_details["reviews"] = reviews
        
        logger.info(f"Successfully processed book: {book_details['title']} by {book_details['author']}")
        return book_details

def main():
    """Main function for testing the scraper."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Enhanced Goodreads Scraper")
    parser.add_argument("--query", help="Book to search for")
    parser.add_argument("--url", help="Goodreads URL to scrape")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    scraper = EnhancedGoodreadsScraper()
    
    if args.query:
        book = scraper.process_book(args.query)
        
        if book and args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(book, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved book data to {args.output}")
    
    elif args.url:
        book_details = scraper.get_book_details(args.url)
        reviews = scraper.get_book_reviews(args.url)
        
        if book_details:
            book_details["reviews"] = reviews
            
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(book_details, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved book data to {args.output}")

if __name__ == "__main__":
    main() 