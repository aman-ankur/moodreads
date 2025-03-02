#!/usr/bin/env python3
"""
Test script for the enhanced data collection and emotional analysis system.

This script demonstrates the integration of Goodreads scraping, Google Books API,
and enhanced emotional analysis to create comprehensive book profiles.
"""

import logging
import sys
import json
from pathlib import Path
import argparse
from pprint import pprint
import time

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from moodreads.scraper.goodreads import GoodreadsScraper
from moodreads.scraper.google_books import GoogleBooksAPIClient
from moodreads.scraper.integrator import BookDataIntegrator
from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.database.mongodb import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('enhanced_data_test.log')
    ]
)
logger = logging.getLogger(__name__)

def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Data saved to {filename}")

def test_goodreads_scraper(url):
    """Test the enhanced Goodreads scraper."""
    logger.info("Testing enhanced Goodreads scraper...")
    
    scraper = GoodreadsScraper()
    
    # Test book scraping
    logger.info(f"Scraping book: {url}")
    book_data = scraper.scrape_book(url)
    
    if book_data:
        logger.info(f"Successfully scraped book: {book_data.get('title', 'Unknown')}")
        save_to_json(book_data, "test_goodreads_book.json")
    else:
        logger.error("Failed to scrape book")
        return None
    
    # Test enhanced reviews
    logger.info("Getting enhanced reviews...")
    reviews = scraper.get_enhanced_reviews(
        url,
        min_rating=3,
        min_words=50,
        max_reviews=10
    )
    
    if reviews:
        logger.info(f"Successfully retrieved {len(reviews)} reviews")
        save_to_json(reviews, "test_goodreads_reviews.json")
    else:
        logger.warning("No reviews found or error retrieving reviews")
    
    return book_data

def test_google_books_api(isbn=None, title=None, author=None):
    """Test the Google Books API client."""
    logger.info("Testing Google Books API client...")
    
    client = GoogleBooksAPIClient()
    
    if isbn:
        logger.info(f"Fetching book by ISBN: {isbn}")
        book_data = client.get_book_by_isbn(isbn)
    elif title and author:
        logger.info(f"Fetching book by title and author: {title} by {author}")
        book_data = client.get_book_by_title_author(title, author)
    else:
        logger.error("Either ISBN or title+author must be provided")
        return None
    
    if book_data:
        logger.info(f"Successfully fetched book: {book_data.get('title', 'Unknown')}")
        save_to_json(book_data, "test_google_books.json")
    else:
        logger.error("Failed to fetch book from Google Books API")
    
    return book_data

def test_data_integration(url):
    """Test the book data integrator."""
    logger.info("Testing book data integration...")
    
    integrator = BookDataIntegrator()
    
    logger.info(f"Integrating data for book: {url}")
    integrated_data = integrator.integrate_book_data(url)
    
    if integrated_data:
        logger.info(f"Successfully integrated data for: {integrated_data.get('title', 'Unknown')}")
        save_to_json(integrated_data, "test_integrated_data.json")
    else:
        logger.error("Failed to integrate book data")
    
    return integrated_data

def test_emotional_analysis(integrated_data):
    """Test the enhanced emotional analyzer."""
    logger.info("Testing enhanced emotional analysis...")
    
    if not integrated_data:
        logger.error("No integrated data provided for analysis")
        return None
    
    analyzer = EmotionalAnalyzer()
    
    # Extract necessary data for analysis
    description = integrated_data.get('description', '')
    reviews = integrated_data.get('reviews', [])
    genres = integrated_data.get('genres', [])
    
    logger.info(f"Analyzing book: {integrated_data.get('title', 'Unknown')}")
    analysis_result = analyzer.analyze_book_enhanced(
        description,
        reviews,
        genres,
        use_cache=False  # Force fresh analysis for testing
    )
    
    if analysis_result:
        logger.info("Successfully analyzed book")
        save_to_json(analysis_result, "test_emotional_analysis.json")
        
        # Print top emotions
        print("\nTop Emotions:")
        for emotion in analysis_result.get('emotional_profile', [])[:5]:
            print(f"- {emotion.get('emotion', 'Unknown')}: {emotion.get('intensity', 0)}/10")
        
        # Print emotional arc
        print("\nEmotional Arc:")
        arc = analysis_result.get('emotional_arc', {})
        print(f"- Beginning: {', '.join(arc.get('beginning', []))}")
        print(f"- Middle: {', '.join(arc.get('middle', []))}")
        print(f"- End: {', '.join(arc.get('end', []))}")
        
        # Print emotional keywords
        print("\nEmotional Keywords:")
        print(f"- {', '.join(analysis_result.get('emotional_keywords', []))}")
    else:
        logger.error("Failed to analyze book")
    
    return analysis_result

def test_mongodb_storage(integrated_data, analysis_result):
    """Test storing the integrated data and analysis in MongoDB."""
    logger.info("Testing MongoDB storage...")
    
    if not integrated_data or not analysis_result:
        logger.error("Missing data for MongoDB storage test")
        return False
    
    try:
        db = MongoDBClient()
        
        # Combine integrated data with analysis result
        book_data = integrated_data.copy()
        book_data.update({
            'emotional_profile': analysis_result.get('emotional_profile', []),
            'emotional_arc': analysis_result.get('emotional_arc', {}),
            'emotional_keywords': analysis_result.get('emotional_keywords', []),
            'unexpected_emotions': analysis_result.get('unexpected_emotions', []),
            'lasting_impact': analysis_result.get('lasting_impact', ''),
            'overall_emotional_profile': analysis_result.get('overall_emotional_profile', ''),
            'emotional_intensity': analysis_result.get('emotional_intensity', 0),
            'embedding': analysis_result.get('embedding', []),
            'enhanced_analysis': True
        })
        
        # Store in MongoDB
        result = db.add_book(book_data)
        
        if result:
            logger.info(f"Successfully stored book in MongoDB with ID: {result}")
            return True
        else:
            logger.error("Failed to store book in MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"Error storing data in MongoDB: {str(e)}")
        return False

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the enhanced data collection and emotional analysis system")
    parser.add_argument("--url", help="Goodreads book URL to test with")
    parser.add_argument("--isbn", help="ISBN to test Google Books API with")
    parser.add_argument("--skip-mongodb", action="store_true", help="Skip MongoDB storage test")
    
    args = parser.parse_args()
    
    # Default URL if none provided
    url = args.url or "https://www.goodreads.com/book/show/40121378-atomic-habits"
    
    try:
        # Step 1: Test Goodreads scraper
        book_data = test_goodreads_scraper(url)
        
        # Step 2: Test Google Books API
        if args.isbn:
            google_data = test_google_books_api(isbn=args.isbn)
        elif book_data and ('isbn' in book_data or 'isbn13' in book_data):
            isbn = book_data.get('isbn13') or book_data.get('isbn')
            google_data = test_google_books_api(isbn=isbn)
        else:
            title = book_data.get('title') if book_data else None
            author = book_data.get('author') if book_data else None
            if title and author:
                google_data = test_google_books_api(title=title, author=author)
            else:
                logger.warning("Skipping Google Books API test due to missing data")
        
        # Step 3: Test data integration
        integrated_data = test_data_integration(url)
        
        # Step 4: Test emotional analysis
        analysis_result = test_emotional_analysis(integrated_data)
        
        # Step 5: Test MongoDB storage (optional)
        if not args.skip_mongodb and integrated_data and analysis_result:
            test_mongodb_storage(integrated_data, analysis_result)
        
        logger.info("All tests completed")
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 