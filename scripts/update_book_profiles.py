#!/usr/bin/env python3
"""
Script to update book emotional profiles with enhanced emotional analysis.
This script processes books in the database and updates their emotional profiles
using the enhanced emotional analysis features.
"""

import argparse
import logging
import sys
import time
from tqdm import tqdm
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import List, Dict
import os
import traceback

from moodreads.scraper.goodreads import GoodreadsScraper
from moodreads.database.mongodb import MongoDBClient
from moodreads.analysis.claude import EmotionalAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_profiles.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def update_book_profiles(batch_size: int = 5, rate_limit: float = 3.0, limit: int = None):
    """
    Update existing books with enhanced emotional profiles and reviews data.
    
    Args:
        batch_size: Number of books to process in each batch
        rate_limit: Minimum seconds between requests
        limit: Maximum number of books to update (None for all)
    """
    try:
        # Initialize components
        logger.info("Initializing components...")
        db = MongoDBClient()
        
        # Fix paths for the extraction scripts
        # Get the absolute path to the scripts directory
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        extract_script_path = os.path.join(scripts_dir, "extract_goodreads_reviews.py")
        emotional_analysis_script = os.path.join(scripts_dir, "emotional_analysis.py")
        
        # Initialize scraper with the correct path
        scraper = GoodreadsScraper()
        scraper.extract_script_path = extract_script_path
        
        # Initialize analyzer
        analyzer = EmotionalAnalyzer()
        
        # Get books without enhanced emotional profiles
        query = {'enhanced_emotional_profile': {'$exists': False}}
        books = list(db.books.find(query))
        
        if limit:
            books = books[:limit]
        
        logger.info(f"Found {len(books)} books to update")
        
        # Process books in batches
        batches = [books[i:i + batch_size] for i in range(0, len(books), batch_size)]
        
        for batch_idx, batch in enumerate(batches):
            logger.info(f"Processing batch {batch_idx+1}/{len(batches)}")
            
            for book in tqdm(batch, desc=f"Batch {batch_idx+1}"):
                book_id = book['_id']
                book_url = book['url']
                title = book['title']
                
                try:
                    logger.info(f"Processing book: {title}")
                    
                    # Get enhanced reviews
                    logger.info(f"Fetching reviews for {title}...")
                    reviews_data = scraper.get_enhanced_reviews(
                        book_url,
                        min_rating=3,  # Only include reviews with 3+ stars
                        min_words=50,  # Only include reviews with at least 50 words
                        max_reviews=10  # Limit to 10 reviews
                    )
                    
                    # Generate enhanced emotional profile
                    logger.info(f"Analyzing emotional profile for {title}...")
                    
                    # Use the analyzer's analyze_book method directly instead of analyze_book_enhanced
                    # since the enhanced method relies on the emotional_analysis.py script
                    reviews_texts = [r.get('text', '') for r in reviews_data.get('reviews', [])]
                    enhanced_analysis = analyzer.analyze_book(
                        book['description'],
                        reviews_texts,
                        book.get('genres', [])
                    )
                    
                    # Add emotional arc and other fields that would normally come from analyze_book_enhanced
                    if 'emotional_profile' in enhanced_analysis and isinstance(enhanced_analysis['emotional_profile'], dict):
                        # Create a simple emotional arc based on the emotional profile
                        emotional_arc = {
                            'beginning': [],
                            'middle': [],
                            'end': []
                        }
                        
                        # Add top emotions to each part of the arc
                        sorted_emotions = sorted(
                            enhanced_analysis['emotional_profile'].items(), 
                            key=lambda x: x[1], 
                            reverse=True
                        )
                        
                        for i, (emotion, _) in enumerate(sorted_emotions[:3]):
                            emotional_arc['beginning'].append(emotion)
                            emotional_arc['middle'].append(emotion)
                            emotional_arc['end'].append(emotion)
                        
                        enhanced_analysis['emotional_arc'] = emotional_arc
                        
                        # Add other fields
                        enhanced_analysis['emotional_keywords'] = list(enhanced_analysis['emotional_profile'].keys())
                        enhanced_analysis['unexpected_emotions'] = []
                        enhanced_analysis['lasting_impact'] = "Generated from book description and reviews"
                        enhanced_analysis['overall_emotional_profile'] = "Generated from book description and reviews"
                    
                    # Update book in database
                    update_data = {
                        'enhanced_emotional_profile': enhanced_analysis,
                        'reviews_data': reviews_data,
                        'emotional_arc': enhanced_analysis.get('emotional_arc', {}),
                        'emotional_keywords': enhanced_analysis.get('emotional_keywords', []),
                        'unexpected_emotions': enhanced_analysis.get('unexpected_emotions', []),
                        'lasting_impact': enhanced_analysis.get('lasting_impact', ''),
                        'overall_emotional_profile': enhanced_analysis.get('overall_emotional_profile', ''),
                        'emotional_intensity': enhanced_analysis.get('emotional_intensity', 0.5),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Keep the original emotional_profile and embedding
                    if 'emotional_profile' in book:
                        update_data['emotional_profile'] = book['emotional_profile']
                    else:
                        update_data['emotional_profile'] = enhanced_analysis.get('emotional_profile', {})
                        
                    if 'embedding' in enhanced_analysis:
                        update_data['embedding'] = enhanced_analysis['embedding']
                    
                    # Update the book in the database
                    db.update_book(str(book_id), update_data)
                    logger.info(f"Updated book: {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing book {title}: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Respect rate limits
                time.sleep(rate_limit)
            
            logger.info(f"Completed batch {batch_idx+1}/{len(batches)}")
            
    except Exception as e:
        logger.error(f"Error updating book profiles: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def main():
    parser = argparse.ArgumentParser(description="Update existing books with enhanced emotional profiles")
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
        "--limit",
        type=int,
        default=None,
        help="Maximum number of books to update (default: all)"
    )
    
    args = parser.parse_args()
    
    try:
        update_book_profiles(
            batch_size=args.batch_size,
            rate_limit=args.rate_limit,
            limit=args.limit
        )
    except KeyboardInterrupt:
        logger.info("Update interrupted by user")
    except Exception as e:
        logger.error(f"Update failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 