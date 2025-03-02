#!/usr/bin/env python3
"""
Script to check the data in the advanced MongoDB database.
This script will connect to the database and display information about the books,
including counts, sample data, and verification of emotional vectors.
"""

import argparse
import logging
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import numpy as np
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB client
from moodreads.database.mongodb import MongoDBClient

def check_database(db_name):
    """
    Check the data in the MongoDB database.
    
    Args:
        db_name: MongoDB database name to check
    """
    try:
        # Set environment variable for MongoDB database name
        os.environ['MONGODB_DB_NAME'] = db_name
        logger.info(f"Checking database: {db_name}")
        
        # Initialize MongoDB client
        db = MongoDBClient()
        
        # Get book count
        book_count = db.books_collection.count_documents({})
        logger.info(f"Total books in database: {book_count}")
        
        if book_count == 0:
            logger.warning("No books found in database")
            return
        
        # Count books with emotional profiles
        books_with_profiles = db.books_collection.count_documents({"emotional_profile": {"$exists": True}})
        logger.info(f"Books with emotional profiles: {books_with_profiles}")
        
        # Count books with embeddings
        books_with_embeddings = db.books_collection.count_documents({"embedding": {"$exists": True}})
        logger.info(f"Books with vector embeddings: {books_with_embeddings}")
        
        # Count books with Google Books data
        books_with_google = db.books_collection.count_documents({"google_id": {"$exists": True}})
        logger.info(f"Books with Google Books data: {books_with_google}")
        
        # Count books with cover images
        books_with_covers = db.books_collection.count_documents({"cover_image": {"$exists": True}})
        logger.info(f"Books with cover images: {books_with_covers}")
        
        # Get a sample book
        sample_book = db.books_collection.find_one({})
        
        if sample_book:
            logger.info("\nSample Book Information:")
            print(f"Title: {sample_book.get('title', 'Unknown')}")
            print(f"Author: {sample_book.get('author', 'Unknown')}")
            print(f"ISBN: {sample_book.get('isbn', 'Unknown')}")
            print(f"Google ID: {sample_book.get('google_id', 'None')}")
            print(f"Cover Image: {'Present' if sample_book.get('cover_image') else 'Missing'}")
            print(f"Genres: {', '.join(sample_book.get('genres', []))}")
            
            # Check emotional profile
            if 'emotional_profile' in sample_book:
                print("\nEmotional Profile:")
                if 'primary_emotions' in sample_book['emotional_profile']:
                    primary_emotions = sample_book['emotional_profile']['primary_emotions']
                    for emotion in primary_emotions[:5]:  # Show first 5 emotions
                        print(f"  {emotion.get('emotion', 'Unknown')}: {emotion.get('intensity', 0)}")
                    if len(primary_emotions) > 5:
                        print(f"  ... and {len(primary_emotions) - 5} more emotions")
                else:
                    print("  No primary emotions found in profile")
            
            # Check embedding
            if 'embedding' in sample_book:
                embedding = sample_book['embedding']
                print(f"\nEmbedding: {len(embedding)} dimensions")
                non_zero = sum(1 for x in embedding if x != 0)
                print(f"Non-zero elements: {non_zero} ({non_zero/len(embedding)*100:.2f}%)")
                
                # Calculate vector magnitude
                magnitude = np.sqrt(sum(x*x for x in embedding))
                print(f"Vector magnitude: {magnitude:.4f}")
                
                # Show a few values
                print("Sample values:", end=" ")
                for i, val in enumerate(embedding[:5]):
                    print(f"{val:.4f}", end=" ")
                print("...")
            
            # Check Google Books data
            if 'google_description' in sample_book:
                print("\nGoogle Books Description:")
                desc = sample_book['google_description']
                print(f"  {desc[:100]}..." if len(desc) > 100 else desc)
            
            # Check reviews
            if 'reviews_data' in sample_book:
                reviews = sample_book['reviews_data']
                print(f"\nReviews: {len(reviews)} total")
                if reviews:
                    sample_review = reviews[0]
                    print(f"Sample review ({sample_review.get('rating', 0)} stars):")
                    review_text = sample_review.get('text', '')
                    print(f"  {review_text[:100]}..." if len(review_text) > 100 else review_text)
        
        logger.info("\nDatabase check completed")
        
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Check the advanced MongoDB database")
    parser.add_argument(
        "--db-name",
        type=str,
        default="moodreads_advanced",
        help="MongoDB database name to check"
    )
    
    args = parser.parse_args()
    
    check_database(args.db_name)

if __name__ == "__main__":
    main() 