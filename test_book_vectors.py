#!/usr/bin/env python3
"""
Test script to process a single book and display the emotional vectors.
This script demonstrates the integration of Goodreads and Google Books data
with emotional analysis.
"""

import json
import argparse
import logging
from pprint import pprint
from bson import ObjectId
from dotenv import load_dotenv

from integrate_emotional_analysis import BookDataIntegrator

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

def process_book(query: str, output_file: str, verbose: bool = False):
    """
    Process a book and display its data and emotional vectors.
    
    Args:
        query: Book title or ISBN to search for
        output_file: File to save the results to
        verbose: Whether to display all book data
    """
    logger.info(f"Processing book: {query}")
    
    # Initialize the integrator
    integrator = BookDataIntegrator()
    
    # Process the book
    book_data = integrator.process_book(query)
    
    if not book_data:
        logger.error(f"Failed to process book: {query}")
        return
    
    # Save to file with custom encoder
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
    
    logger.info(f"Saved book data to: {output_file}")
    
    # Display book information
    print("\n" + "="*80)
    print(f"BOOK: {book_data['title']} by {book_data['author']}")
    print("="*80)
    
    # Display Goodreads data
    print("\n--- GOODREADS DATA ---")
    print(f"Goodreads ID: {book_data.get('goodreads_id', 'N/A')}")
    print(f"URL: {book_data.get('goodreads_url', 'N/A')}")
    print(f"Cover: {book_data.get('cover_url', 'N/A')}")
    print(f"Rating: {book_data.get('avg_rating', 'N/A')} ({book_data.get('ratings_count', 0)} ratings)")
    print(f"ISBN: {book_data.get('isbn', 'N/A')}")
    print(f"Genres: {', '.join(book_data.get('genres', []))}")
    
    # Display Google Books data
    print("\n--- GOOGLE BOOKS DATA ---")
    print(f"Google Books ID: {book_data.get('google_books_id', 'N/A')}")
    print(f"Google Books Link: {book_data.get('google_books_link', 'N/A')}")
    
    # Display emotional vectors
    print("\n--- EMOTIONAL VECTORS ---")
    emotional_profile = book_data.get('emotional_profile', {})
    
    # Primary emotions (vectors)
    print("\nPrimary Emotions (Vectors):")
    for emotion in emotional_profile.get('primary_emotions', []):
        print(f"  {emotion['emotion']}: {emotion['intensity']}/10")
    
    # Emotional arc
    print("\nEmotional Arc:")
    for stage, emotions in emotional_profile.get('emotional_arc', {}).items():
        print(f"  {stage.capitalize()}: {', '.join(emotions[:3])}")
    
    # Unexpected emotions
    print("\nUnexpected Emotions:")
    print(f"  {', '.join(emotional_profile.get('unexpected_emotions', ['None']))}")
    
    # Emotional keywords
    print("\nEmotional Keywords:")
    print(f"  {', '.join(emotional_profile.get('emotional_keywords', ['None']))}")
    
    # Overall profile
    print("\nOverall Emotional Profile:")
    print(f"  {emotional_profile.get('overall_emotional_profile', 'N/A')}")
    
    # Display reviews if verbose
    if verbose and 'reviews' in book_data:
        print("\n--- REVIEWS ---")
        for i, review in enumerate(book_data['reviews'][:3]):  # Show first 3 reviews
            print(f"\nReview {i+1} by {review.get('reviewer', 'Anonymous')} ({review.get('rating', 'N/A')}/5):")
            print(f"  {review.get('text', '')[:200]}..." if len(review.get('text', '')) > 200 else review.get('text', ''))
    
    # Display full book data if verbose
    if verbose:
        print("\n--- FULL BOOK DATA ---")
        # Remove large text fields for cleaner output
        display_data = book_data.copy()
        if 'description' in display_data:
            display_data['description'] = display_data['description'][:100] + "..." if display_data['description'] else ""
        if 'reviews' in display_data:
            for review in display_data['reviews']:
                if 'text' in review:
                    review['text'] = review['text'][:50] + "..." if review['text'] else ""
        pprint(display_data)
    
    print("\n" + "="*80)
    print(f"Book processing complete. Data saved to {output_file}")
    print("="*80 + "\n")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process a book and display its emotional vectors')
    parser.add_argument('query', help='Book title or ISBN to search for')
    parser.add_argument('--output', default='book_data.json', help='Output JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Display all book data')
    
    args = parser.parse_args()
    
    process_book(args.query, args.output, args.verbose)

if __name__ == '__main__':
    main() 