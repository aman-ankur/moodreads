#!/usr/bin/env python3
"""
Script to check book details and emotional analysis.
"""

from pymongo import MongoClient
import json
from bson.objectid import ObjectId

def check_book(book_id):
    """Check book details and emotional analysis."""
    client = MongoClient()
    db = client['moodreads_production']
    
    # Convert string ID to ObjectId
    book = db.books.find_one({'_id': ObjectId(book_id)})
    
    if not book:
        print(f"Book with ID {book_id} not found")
        return
    
    print(f"Book found: {book_id}")
    print(f"Title: {book.get('title')}")
    print(f"Author: {book.get('author')}")
    print(f"Has emotional_analysis: {'emotional_analysis' in book}")
    
    if 'emotional_analysis' in book:
        emotional_analysis = book['emotional_analysis']
        print("\nEmotional Analysis:")
        
        # Print emotional profile
        if 'emotional_profile' in emotional_analysis:
            print("\nEmotional Profile:")
            for emotion in emotional_analysis['emotional_profile']:
                print(f"  - {emotion.get('emotion')}: {emotion.get('intensity')}")
        
        # Print emotional keywords
        if 'emotional_keywords' in emotional_analysis:
            print("\nEmotional Keywords:")
            print(f"  {', '.join(emotional_analysis['emotional_keywords'])}")
        
        # Print overall emotional profile
        if 'overall_emotional_profile' in emotional_analysis:
            print("\nOverall Emotional Profile:")
            print(f"  {emotional_analysis['overall_emotional_profile']}")
        
        # Print emotional intensity
        if 'emotional_intensity' in emotional_analysis:
            print("\nEmotional Intensity:")
            print(f"  {emotional_analysis['emotional_intensity']}")
        
        # Check if embedding exists
        if 'embedding' in emotional_analysis:
            print("\nEmbedding exists with length:", len(emotional_analysis['embedding']))
    else:
        print("\nNo emotional analysis found for this book")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python check_book.py <book_id>")
        sys.exit(1)
    
    book_id = sys.argv[1]
    check_book(book_id) 