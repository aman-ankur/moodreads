#!/usr/bin/env python3
"""
Script to update books in the database with enhanced emotional profiles.

This script processes books in the database that don't yet have enhanced
emotional analysis, fetching additional data from Google Books when needed
and generating comprehensive emotional profiles.
"""

import logging
import sys
import json
import argparse
from pathlib import Path
import time
from datetime import datetime
import traceback

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
        logging.FileHandler('update_emotional_profiles.log')
    ]
)
logger = logging.getLogger(__name__)

class EmotionalProfileUpdater:
    """
    Updates existing books with enhanced emotional profiles.
    """
    
    def __init__(self, batch_size: int = 10, rate_limit: float = 3.0):
        """
        Initialize the updater.
        
        Args:
            batch_size: Number of books to process in each batch
            rate_limit: Minimum seconds between processing books
        """
        self.db = MongoDBClient()
        self.integrator = BookDataIntegrator()
        self.analyzer = EmotionalAnalyzer()
        self.google_books_client = GoogleBooksAPIClient()
        self.goodreads_scraper = GoodreadsScraper()
        
        self.batch_size = batch_size
        self.rate_limit = rate_limit
        self.last_process_time = 0
        
        logger.info(f"EmotionalProfileUpdater initialized with batch size {batch_size}")
    
    def _respect_rate_limit(self) -> None:
        """Ensure we respect the rate limit between processing books."""
        elapsed = time.time() - self.last_process_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_process_time = time.time()
    
    def get_books_to_update(self, limit: int = None, skip_enhanced: bool = True) -> list:
        """
        Get books from the database that need emotional profile updates.
        
        Args:
            limit: Maximum number of books to return
            skip_enhanced: Whether to skip books that already have enhanced analysis
            
        Returns:
            List of books to update
        """
        query = {}
        
        # Skip books that already have enhanced analysis if requested
        if skip_enhanced:
            query['enhanced_analysis'] = {'$ne': True}
        
        # Get books sorted by rating (highest first) to prioritize popular books
        books = list(self.db.books_collection.find(
            query,
            sort=[('rating', -1)],
            limit=limit or self.batch_size
        ))
        
        logger.info(f"Found {len(books)} books to update")
        return books
    
    def update_book(self, book: dict) -> bool:
        """
        Update a book with enhanced emotional analysis.
        
        Args:
            book: Book document from the database
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            book_id = book['_id']
            title = book.get('title', 'Unknown')
            author = book.get('author', 'Unknown')
            
            logger.info(f"Updating book: {title} by {author}")
            
            # Step 1: Check if we need to get additional data
            need_additional_data = False
            
            # Check if we have a description
            if 'description' not in book or not book['description'] or len(book['description']) < 100:
                need_additional_data = True
                logger.info(f"Book needs additional data: missing or short description")
            
            # Check if we have reviews
            if 'reviews' not in book or not book['reviews'] or len(book['reviews']) < 3:
                need_additional_data = True
                logger.info(f"Book needs additional data: missing or few reviews")
            
            # Step 2: Get additional data if needed
            if need_additional_data:
                # Try to get data from Google Books if we have an ID
                if 'google_books_id' in book:
                    logger.info(f"Fetching additional data from Google Books using volume ID: {book['google_books_id']}")
                    google_data = self.google_books_client.get_book_by_volume_id(book['google_books_id'])
                    
                    if google_data:
                        # Update book with Google Books data
                        for key, value in google_data.items():
                            # Skip fields we already have
                            if key in ['title', 'author', 'isbn', 'isbn13'] and key in book:
                                continue
                            
                            # Add Google Books specific fields
                            book[key] = value
                        
                        # Use Google description if it's better
                        if 'google_description' in google_data and (
                            'description' not in book or 
                            len(book.get('description', '')) < len(google_data['google_description'])
                        ):
                            book['description'] = google_data['google_description']
                            logger.info(f"Updated book description from Google Books")
                
                # Try to get data from Goodreads if we have a URL
                if 'goodreads_url' in book and (
                    'reviews' not in book or 
                    not book['reviews'] or 
                    len(book['reviews']) < 3
                ):
                    logger.info(f"Fetching additional reviews from Goodreads: {book['goodreads_url']}")
                    reviews = self.goodreads_scraper.get_enhanced_reviews(
                        book['goodreads_url'],
                        min_rating=3,
                        min_words=50,
                        max_reviews=20
                    )
                    
                    if reviews:
                        book['reviews'] = reviews
                        logger.info(f"Updated book with {len(reviews)} reviews from Goodreads")
            
            # Step 3: Create analysis text if it doesn't exist
            if 'analysis_text' not in book or not book['analysis_text']:
                logger.info(f"Creating analysis text for book")
                
                text_parts = []
                
                # Add book description
                if 'description' in book and book['description']:
                    text_parts.append(f"Book Description: {book['description']}")
                
                # Add sample text if available
                if 'sample_text' in book and book['sample_text']:
                    text_parts.append(f"Sample Text: {book['sample_text']}")
                
                # Add text snippet if available
                if 'text_snippet' in book and book['text_snippet']:
                    text_parts.append(f"Text Snippet: {book['text_snippet']}")
                
                # Add quotes
                if 'quotes' in book and book['quotes']:
                    quotes_text = "\n".join([f"- {quote}" for quote in book['quotes'][:5]])
                    text_parts.append(f"Notable Quotes:\n{quotes_text}")
                
                # Add reviews
                if 'reviews' in book and book['reviews']:
                    reviews_text = "\n\n".join([
                        f"Review ({review.get('rating', 0)}/5 stars): {review.get('text', '')}" 
                        for review in book['reviews'][:10]
                    ])
                    text_parts.append(f"Reader Reviews:\n{reviews_text}")
                
                book['analysis_text'] = "\n\n".join(text_parts)
            
            # Step 4: Perform emotional analysis
            logger.info(f"Performing emotional analysis for book")
            
            # Extract necessary data for analysis
            description = book.get('description', '')
            reviews = book.get('reviews', [])
            genres = book.get('genres', [])
            
            # Generate a book ID for caching if needed
            if 'isbn13' in book:
                book_id_for_cache = f"isbn13_{book['isbn13']}"
            elif 'isbn' in book:
                book_id_for_cache = f"isbn_{book['isbn']}"
            elif 'google_books_id' in book:
                book_id_for_cache = f"google_{book['google_books_id']}"
            else:
                book_id_for_cache = f"title_{book.get('title', '').replace(' ', '_')}"
            
            # Perform analysis
            analysis_result = self.analyzer.analyze_book_enhanced(
                description,
                reviews,
                genres,
                use_cache=True,
                book_id=book_id_for_cache
            )
            
            if not analysis_result:
                logger.error(f"Failed to analyze book: {title}")
                return False
            
            # Step 5: Update book with analysis results
            book.update({
                'emotional_profile': analysis_result.get('emotional_profile', []),
                'emotional_arc': analysis_result.get('emotional_arc', {}),
                'emotional_keywords': analysis_result.get('emotional_keywords', []),
                'unexpected_emotions': analysis_result.get('unexpected_emotions', []),
                'lasting_impact': analysis_result.get('lasting_impact', ''),
                'overall_emotional_profile': analysis_result.get('overall_emotional_profile', ''),
                'emotional_intensity': analysis_result.get('emotional_intensity', 0),
                'embedding': analysis_result.get('embedding', []).tolist() if hasattr(analysis_result.get('embedding', []), 'tolist') else analysis_result.get('embedding', []),
                'enhanced_analysis': True,
                'analysis_updated_at': datetime.now().isoformat()
            })
            
            # Step 6: Save updated book to database
            result = self.db.books_collection.update_one(
                {'_id': book_id},
                {'$set': book}
            )
            
            if result.modified_count > 0:
                logger.info(f"Successfully updated book: {title}")
                return True
            else:
                logger.warning(f"No changes made to book: {title}")
                return False
            
        except Exception as e:
            logger.error(f"Error updating book {book.get('title', 'Unknown')}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def update_books(self, limit: int = None, skip_enhanced: bool = True) -> dict:
        """
        Update multiple books with enhanced emotional profiles.
        
        Args:
            limit: Maximum number of books to update
            skip_enhanced: Whether to skip books that already have enhanced analysis
            
        Returns:
            Dictionary with update statistics
        """
        stats = {
            'total': 0,
            'success': 0,
            'failure': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Get books to update
        books = self.get_books_to_update(limit, skip_enhanced)
        stats['total'] = len(books)
        
        # Process each book
        for i, book in enumerate(books, 1):
            logger.info(f"Processing book {i}/{len(books)}")
            
            # Respect rate limit
            self._respect_rate_limit()
            
            # Update book
            success = self.update_book(book)
            
            if success:
                stats['success'] += 1
            else:
                stats['failure'] += 1
        
        # Add end time
        stats['end_time'] = datetime.now().isoformat()
        
        # Log statistics
        logger.info(f"Update completed: {stats['success']}/{stats['total']} books updated successfully")
        
        return stats

def main():
    """Main function to run the updater."""
    parser = argparse.ArgumentParser(description="Update books with enhanced emotional profiles")
    parser.add_argument("--limit", type=int, help="Maximum number of books to update")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of books to process in each batch")
    parser.add_argument("--include-enhanced", action="store_true", help="Include books that already have enhanced analysis")
    
    args = parser.parse_args()
    
    try:
        # Initialize updater
        updater = EmotionalProfileUpdater(batch_size=args.batch_size)
        
        # Update books
        stats = updater.update_books(
            limit=args.limit,
            skip_enhanced=not args.include_enhanced
        )
        
        # Print statistics
        print("\nUpdate Statistics:")
        print(f"Total books processed: {stats['total']}")
        print(f"Successfully updated: {stats['success']}")
        print(f"Failed to update: {stats['failure']}")
        
    except KeyboardInterrupt:
        logger.info("Update interrupted by user")
        print("\nUpdate interrupted by user")
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\nError during update: {str(e)}")

if __name__ == "__main__":
    main() 