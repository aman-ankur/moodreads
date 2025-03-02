#!/usr/bin/env python3
"""
Test script for the MoodReads integration system.
This script tests the integration of Goodreads scraping with Google Books emotional analysis.
"""

import os
import json
import argparse
import logging
from dotenv import load_dotenv
from bson import ObjectId
from pymongo import MongoClient

from integrate_emotional_analysis import BookDataIntegrator
from google_books_emotional_analysis import GoogleBooksClient, EmotionalAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Custom JSON encoder to handle MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def test_single_book(query: str, output_file: str):
    """Test processing a single book."""
    logger.info(f"Testing single book processing for: {query}")
    
    integrator = BookDataIntegrator()
    book_data = integrator.process_book(query)
    
    if book_data:
        logger.info(f"Successfully processed book: {book_data['title']} by {book_data['author']}")
        
        # Save to file with custom encoder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
        
        logger.info(f"Saved book data to: {output_file}")
        
        # Display emotional profile summary
        print("\n=== Emotional Profile Summary ===\n")
        print(f"Book: {book_data['title']} by {book_data['author']}")
        
        print("\nTop Emotions:")
        for emotion in book_data['emotional_profile']['primary_emotions'][:5]:
            print(f"- {emotion['emotion']}: {emotion['intensity']}/10")
        
        print(f"\nOverall Profile: {book_data['emotional_profile']['overall_emotional_profile']}")
        
        if 'unexpected_emotions' in book_data['emotional_profile']:
            print(f"\nUnexpected Emotions: {', '.join(book_data['emotional_profile']['unexpected_emotions'])}")
        
        # Display vector information
        print("\n=== Vector Information ===\n")
        print("Emotional Vectors:")
        for emotion in book_data['emotional_profile']['primary_emotions']:
            print(f"- {emotion['emotion']}: {emotion['intensity']}")
        
        # Show MongoDB storage details
        print("\n=== MongoDB Storage Details ===\n")
        print(f"MongoDB ID: {book_data.get('_id')}")
        print(f"Created At: {book_data.get('created_at')}")
        print(f"Last Updated: {book_data.get('last_updated')}")
        
        return True
    else:
        logger.error(f"Failed to process book: {query}")
        return False

def test_google_books_id(book_id: str, output_file: str):
    """Test processing a book directly from Google Books using a Google Books ID."""
    logger.info(f"Testing direct Google Books processing for ID: {book_id}")
    
    # Initialize clients
    google_books_client = GoogleBooksClient()
    emotional_analyzer = EmotionalAnalyzer()
    
    # Get book from Google Books
    book = google_books_client.get_book_by_id(book_id)
    if not book:
        logger.error(f"Failed to find book with Google Books ID: {book_id}")
        return False
    
    logger.info(f"Found book: {book['title']} by {', '.join(book['authors'])}")
    
    # Create emotional profile
    emotional_profile = emotional_analyzer.create_emotional_profile(book)
    book['emotional_profile'] = emotional_profile
    
    # Format for output
    formatted_book = {
        'title': book['title'],
        'author': ', '.join(book['authors']),
        'isbn': book['isbn'],
        'description': book['description'],
        'genres': book['categories'],
        'google_books_id': book['id'],
        'google_books_link': book['info_link'],
        'cover_url': book['image_links'].get('thumbnail'),
        'emotional_profile': emotional_profile
    }
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_book, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved book data to: {output_file}")
    
    # Display emotional profile summary
    print("\n=== Emotional Profile Summary ===\n")
    print(f"Book: {formatted_book['title']} by {formatted_book['author']}")
    
    print("\nTop Emotions:")
    for emotion in emotional_profile['primary_emotions'][:5]:
        print(f"- {emotion['emotion']}: {emotion['intensity']}/10")
    
    print(f"\nOverall Profile: {emotional_profile['overall_emotional_profile']}")
    
    if 'unexpected_emotions' in emotional_profile:
        print(f"\nUnexpected Emotions: {', '.join(emotional_profile['unexpected_emotions'])}")
    
    return True

def test_mood_recommendations(mood: str, output_file: str):
    """Test mood-based recommendations."""
    logger.info(f"Testing mood recommendations for: {mood}")
    
    integrator = BookDataIntegrator()
    recommendations = integrator.get_mood_recommendations(mood)
    
    if recommendations:
        logger.info(f"Found {len(recommendations)} recommendations for mood: {mood}")
        
        # Save to file with custom encoder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
        
        logger.info(f"Saved recommendations to: {output_file}")
        
        # Display recommendations
        print(f"\n=== Book Recommendations for Mood: '{mood}' ===\n")
        for i, rec in enumerate(recommendations):
            print(f"{i+1}. {rec['title']} by {rec['author']}")
            print(f"   Match Score: {rec['match_score']}")
            print(f"   Matching Emotions: {', '.join([e['emotion'] for e in rec['matching_emotions']])}")
            print()
        
        return True
    else:
        logger.warning(f"No recommendations found for mood: {mood}")
        return False

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Test the MoodReads integration system')
    parser.add_argument('--book', help='Test processing a single book')
    parser.add_argument('--google-id', help='Test processing a book directly from Google Books using ID')
    parser.add_argument('--mood', help='Test mood-based recommendations')
    parser.add_argument('--output', default='test_output.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    if args.book:
        test_single_book(args.book, args.output)
    elif args.google_id:
        test_google_books_id(args.google_id, args.output)
    elif args.mood:
        test_mood_recommendations(args.mood, args.output)
    else:
        # Run a default test
        print("=== Running Default Test ===")
        print("1. Processing 'To Kill a Mockingbird'")
        success1 = test_single_book("To Kill a Mockingbird", "mockingbird_test.json")
        
        if success1:
            print("\n2. Testing mood recommendations for 'inspiring and uplifting'")
            test_mood_recommendations("inspiring and uplifting", "inspiring_books.json")
        
        print("\nTests completed.")

if __name__ == '__main__':
    main() 