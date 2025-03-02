#!/usr/bin/env python3
"""
Test script for the enhanced recommendation engine.

This script demonstrates the enhanced recommendation capabilities
based on emotional profiles and user mood queries.
"""

import logging
import sys
import json
import argparse
from pathlib import Path
from pprint import pprint
import time

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from moodreads.recommendation.enhanced_recommender import EnhancedRecommender
from moodreads.database.mongodb import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_recommendations.log')
    ]
)
logger = logging.getLogger(__name__)

def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Data saved to {filename}")

def test_mood_query(query, limit=5):
    """Test the recommendation engine with a mood query."""
    logger.info(f"Testing mood query: '{query}'")
    
    recommender = EnhancedRecommender()
    
    # Get recommendations
    start_time = time.time()
    recommendations = recommender.recommend_books(
        query=query,
        limit=limit,
        min_rating=3.5,
        include_explanation=True
    )
    elapsed_time = time.time() - start_time
    
    if recommendations:
        logger.info(f"Found {len(recommendations)} recommendations in {elapsed_time:.2f} seconds")
        
        # Save to JSON
        filename = f"recommendations_{query.replace(' ', '_')[:30]}.json"
        save_to_json(recommendations, filename)
        
        # Print recommendations
        print(f"\nRecommendations for query: '{query}'")
        print(f"Found {len(recommendations)} recommendations in {elapsed_time:.2f} seconds\n")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['title']} by {rec['author']}")
            print(f"   Similarity score: {rec['similarity_score']:.2f}")
            print(f"   Top emotions: {', '.join([e['emotion'] for e in rec.get('emotional_profile', [])])}")
            print(f"   Explanation: {rec.get('explanation', 'No explanation available')}")
            print()
    else:
        logger.warning(f"No recommendations found for query: '{query}'")
        print(f"\nNo recommendations found for query: '{query}'")
    
    return recommendations

def test_similar_books(book_id, limit=5):
    """Test finding books with similar emotional profiles."""
    logger.info(f"Testing similar books for book ID: {book_id}")
    
    # Get book title for reference
    db = MongoDBClient()
    book = db.books_collection.find_one({'_id': book_id}, {'title': 1, 'author': 1})
    
    if not book:
        logger.error(f"Book not found with ID: {book_id}")
        print(f"Book not found with ID: {book_id}")
        return []
    
    book_title = book.get('title', 'Unknown')
    book_author = book.get('author', 'Unknown')
    
    recommender = EnhancedRecommender()
    
    # Get similar books
    start_time = time.time()
    similar_books = recommender.get_similar_books(
        book_id=book_id,
        limit=limit
    )
    elapsed_time = time.time() - start_time
    
    if similar_books:
        logger.info(f"Found {len(similar_books)} similar books in {elapsed_time:.2f} seconds")
        
        # Save to JSON
        filename = f"similar_books_{book_id}.json"
        save_to_json(similar_books, filename)
        
        # Print similar books
        print(f"\nBooks similar to '{book_title}' by {book_author}")
        print(f"Found {len(similar_books)} similar books in {elapsed_time:.2f} seconds\n")
        
        for i, book in enumerate(similar_books, 1):
            print(f"{i}. {book['title']} by {book['author']}")
            print(f"   Similarity score: {book['similarity_score']:.2f}")
            print(f"   Common emotions: {', '.join(book.get('common_emotions', []))}")
            print(f"   Top emotions: {', '.join([e['emotion'] for e in book.get('emotional_profile', [])])}")
            print()
    else:
        logger.warning(f"No similar books found for book ID: {book_id}")
        print(f"\nNo similar books found for book ID: {book_id}")
    
    return similar_books

def test_predefined_queries():
    """Test the recommendation engine with predefined mood queries."""
    predefined_queries = [
        "I'm feeling sad and need something uplifting",
        "I want a thrilling book that will keep me on the edge of my seat",
        "I'm looking for a book that will make me feel nostalgic",
        "I need something calming and peaceful to read before bed",
        "I want to feel inspired and motivated",
        "I'm in the mood for a book that will make me laugh",
        "I want a book that explores deep emotions and human connections",
        "I'm feeling anxious and need something comforting",
        "I want to experience a sense of wonder and awe",
        "I'm looking for a book with a journey from darkness to hope"
    ]
    
    results = {}
    
    for query in predefined_queries:
        recommendations = test_mood_query(query)
        results[query] = len(recommendations)
    
    # Print summary
    print("\nSummary of predefined queries:")
    for query, count in results.items():
        print(f"- '{query}': {count} recommendations")
    
    return results

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the enhanced recommendation engine")
    parser.add_argument("--query", help="Mood query to test")
    parser.add_argument("--book-id", help="Book ID to find similar books for")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of recommendations to return")
    parser.add_argument("--predefined", action="store_true", help="Test predefined mood queries")
    
    args = parser.parse_args()
    
    try:
        if args.predefined:
            test_predefined_queries()
        elif args.query:
            test_mood_query(args.query, args.limit)
        elif args.book_id:
            test_similar_books(args.book_id, args.limit)
        else:
            print("Please specify either --query, --book-id, or --predefined")
            parser.print_help()
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 