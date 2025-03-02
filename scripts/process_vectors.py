#!/usr/bin/env python3
"""
Script to process books and generate vector embeddings.

This script processes books in the database to generate and store vector embeddings
for their emotional profiles, enabling efficient similarity-based recommendations.
"""

import os
import sys
import logging
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodreads.analysis.vector_embeddings import VectorEmbeddingStore
from moodreads.database.mongodb import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/vector_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_all_books():
    """Process all books with emotional profiles to generate vector embeddings."""
    vector_store = VectorEmbeddingStore()
    total, success = vector_store.process_all_books()
    
    logger.info(f"Processed {total} books, {success} successful")
    print(f"Processed {total} books, {success} successful")

def process_book(book_id: str):
    """
    Process a specific book to generate vector embeddings.
    
    Args:
        book_id: MongoDB ID of the book
    """
    vector_store = VectorEmbeddingStore()
    db = MongoDBClient()
    
    # Get book
    book = db.get_book(book_id)
    
    if not book:
        logger.error(f"Book not found with ID: {book_id}")
        print(f"Book not found with ID: {book_id}")
        return
    
    # Process book
    success = vector_store.process_book_for_vectors(book)
    
    if success:
        logger.info(f"Successfully processed book: {book.get('title', 'Unknown')}")
        print(f"Successfully processed book: {book.get('title', 'Unknown')}")
    else:
        logger.error(f"Failed to process book: {book.get('title', 'Unknown')}")
        print(f"Failed to process book: {book.get('title', 'Unknown')}")

def test_recommendations(mood_query: str, limit: int = 5):
    """
    Test getting recommendations by mood.
    
    Args:
        mood_query: Mood query
        limit: Maximum number of recommendations
    """
    vector_store = VectorEmbeddingStore()
    recommendations = vector_store.get_recommendations_by_mood(mood_query, limit)
    
    if not recommendations:
        logger.warning(f"No recommendations found for mood: {mood_query}")
        print(f"No recommendations found for mood: {mood_query}")
        return
    
    logger.info(f"Found {len(recommendations)} recommendations for mood: {mood_query}")
    print(f"\n=== Book Recommendations for Mood: '{mood_query}' ===\n")
    
    for i, rec in enumerate(recommendations):
        print(f"{i+1}. {rec['title']} by {rec['author']}")
        print(f"   Match Score: {rec['match_score']}%")
        
        if rec.get('matching_emotions'):
            print(f"   Matching Emotions:")
            for emotion in rec['matching_emotions'][:3]:
                print(f"     - {emotion['emotion']}: {emotion['intensity']}/10")
        
        print()

def test_similar_books(book_id: str, limit: int = 5):
    """
    Test finding books similar to a given book.
    
    Args:
        book_id: MongoDB ID of the reference book
        limit: Maximum number of similar books to return
    """
    vector_store = VectorEmbeddingStore()
    db = MongoDBClient()
    
    # Get reference book
    reference_book = db.get_book(book_id)
    
    if not reference_book:
        logger.error(f"Reference book not found with ID: {book_id}")
        print(f"Reference book not found with ID: {book_id}")
        return
    
    # Find similar books
    similar_books = vector_store.find_similar_books(book_id, limit)
    
    if not similar_books:
        logger.warning(f"No similar books found for: {reference_book.get('title', 'Unknown')}")
        print(f"No similar books found for: {reference_book.get('title', 'Unknown')}")
        return
    
    logger.info(f"Found {len(similar_books)} books similar to: {reference_book.get('title', 'Unknown')}")
    print(f"\n=== Books Similar to '{reference_book.get('title', 'Unknown')}' ===\n")
    
    for i, book in enumerate(similar_books):
        print(f"{i+1}. {book['title']} by {book['author']}")
        print(f"   Similarity Score: {book['similarity_score']}%")
        print()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process books and generate vector embeddings")
    
    # Add arguments
    parser.add_argument("--process-all", action="store_true", help="Process all books with emotional profiles")
    parser.add_argument("--process-book", help="Process a specific book by ID")
    parser.add_argument("--test-recommendations", help="Test recommendations for a mood query")
    parser.add_argument("--test-similar-books", help="Test finding books similar to a given book by ID")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    
    args = parser.parse_args()
    
    if args.process_all:
        process_all_books()
    elif args.process_book:
        process_book(args.process_book)
    elif args.test_recommendations:
        test_recommendations(args.test_recommendations, args.limit)
    elif args.test_similar_books:
        test_similar_books(args.test_similar_books, args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 