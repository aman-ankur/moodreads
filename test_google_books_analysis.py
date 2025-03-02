#!/usr/bin/env python3
"""
Test script for Google Books emotional analysis.
This script demonstrates how to use the GoogleBooksClient and EmotionalAnalyzer classes.
"""

import json
import argparse
from google_books_emotional_analysis import GoogleBooksClient, EmotionalAnalyzer

def test_book_search(query, max_results=3):
    """Test searching for books."""
    client = GoogleBooksClient()
    books = client.search_book(query, max_results=max_results)
    
    print(f"\n=== Found {len(books)} books for query: '{query}' ===\n")
    
    for i, book in enumerate(books):
        print(f"{i+1}. {book['title']} by {', '.join(book['authors'] if book['authors'] else ['Unknown'])}")
        print(f"   ID: {book['id']}")
        print(f"   ISBN: {book['isbn']}")
        print(f"   Categories: {', '.join(book['categories'] if book['categories'] else ['Unknown'])}")
        print(f"   Rating: {book['average_rating']} ({book['ratings_count']} ratings)")
        print(f"   Description: {book['description'][:150]}..." if book['description'] else "   No description available")
        print()
    
    return books

def test_book_reviews(book_id):
    """Test getting book reviews."""
    client = GoogleBooksClient()
    reviews = client.get_book_reviews(book_id)
    
    print(f"\n=== Found {len(reviews)} reviews for book ID: {book_id} ===\n")
    
    for i, review in enumerate(reviews):
        print(f"Review {i+1}:")
        print(f"Source: {review.get('source', 'Unknown')}")
        print(f"Rating: {review.get('rating', 'Unknown')}")
        print(f"Text: {review.get('text', 'No text')[:200]}...")
        print()
    
    return reviews

def test_emotional_analysis(book_id, save_to_file=None):
    """Test emotional analysis of a book."""
    client = GoogleBooksClient()
    analyzer = EmotionalAnalyzer()
    
    # Get book data
    book = client.get_book_by_id(book_id)
    if not book:
        print(f"Book with ID {book_id} not found")
        return
    
    print(f"\n=== Analyzing book: {book['title']} by {', '.join(book['authors'] if book['authors'] else ['Unknown'])} ===\n")
    
    # Get reviews
    book['reviews'] = client.get_book_reviews(book_id)
    
    # Create emotional profile
    emotional_profile = analyzer.create_emotional_profile(book)
    
    # Add emotional profile to book data
    book['emotional_profile'] = emotional_profile
    
    # Print summary
    print("Top Emotions:")
    for emotion in emotional_profile['primary_emotions'][:5]:
        print(f"- {emotion['emotion']}: {emotion['intensity']}/10")
    
    print("\nEmotional Arc:")
    for stage, emotions in emotional_profile['emotional_arc'].items():
        print(f"- {stage.capitalize()}: {', '.join(emotions[:3])}")
    
    print(f"\nUnexpected Emotions: {', '.join(emotional_profile['unexpected_emotions'][:5])}")
    
    print(f"\nLasting Impact: {emotional_profile['lasting_impact']}")
    
    print("\nEmotional Keywords:")
    print(', '.join(emotional_profile['emotional_keywords'][:10]))
    
    print(f"\nOverall Profile: {emotional_profile['overall_emotional_profile']}")
    
    # Save to file if requested
    if save_to_file:
        with open(save_to_file, 'w', encoding='utf-8') as f:
            json.dump(book, f, indent=2, ensure_ascii=False)
        print(f"\nSaved analysis to {save_to_file}")
    
    return book

def main():
    parser = argparse.ArgumentParser(description='Test Google Books emotional analysis')
    parser.add_argument('--search', help='Search for books by title/author')
    parser.add_argument('--reviews', help='Get reviews for a book by ID')
    parser.add_argument('--analyze', help='Analyze a book by ID')
    parser.add_argument('--output', help='Output file for analysis results')
    
    args = parser.parse_args()
    
    if args.search:
        books = test_book_search(args.search)
        # If analyze flag not set, analyze the first book found
        if not args.analyze and books:
            args.analyze = books[0]['id']
    
    if args.reviews:
        test_book_reviews(args.reviews)
    
    if args.analyze:
        test_emotional_analysis(args.analyze, args.output)

if __name__ == '__main__':
    main() 