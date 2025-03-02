#!/usr/bin/env python3
"""
Debug script to analyze what's happening with the user query analysis.
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.analysis.vector_embeddings import VectorEmbeddingStore
from moodreads.database.mongodb import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def debug_query_analysis(mood_query: str):
    """
    Debug the query analysis process.
    
    Args:
        mood_query: User's mood query
    """
    print(f"\n=== Debugging Query Analysis for: '{mood_query}' ===\n")
    
    # Initialize components
    analyzer = EmotionalAnalyzer()
    vector_store = VectorEmbeddingStore()
    db = MongoDBClient()
    
    # Step 1: Check if there are books with emotional profiles
    books_with_profiles = db.books_collection.count_documents({'emotional_profile': {'$exists': True}})
    print(f"Books with emotional profiles: {books_with_profiles}")
    
    # Step 2: Check if there are books with embeddings
    books_with_embeddings = db.books_collection.count_documents({'embedding': {'$exists': True}})
    print(f"Books with vector embeddings: {books_with_embeddings}")
    
    # Step 3: Analyze the user query
    print(f"\nAnalyzing query: '{mood_query}'")
    try:
        query_analysis = analyzer.analyze_user_query(mood_query)
        print("\nQuery analysis result:")
        print(json.dumps(query_analysis, indent=2))
        
        # Check if primary emotions exist
        if 'primary_emotions' not in query_analysis or not query_analysis['primary_emotions']:
            print("\n⚠️ WARNING: No primary emotions found in query analysis!")
        else:
            print(f"\nFound {len(query_analysis['primary_emotions'])} primary emotions in query analysis.")
        
        # Step 4: Generate vector for query
        print("\nGenerating vector for query...")
        query_vector = vector_store.generate_emotion_vector(query_analysis)
        print(f"Vector dimensions: {len(query_vector)}")
        print(f"Vector non-zero elements: {sum(1 for x in query_vector if x > 0)}")
        print(f"Vector sample: {query_vector[:5]}...")
        
        # Step 5: Check if there are any books that match
        print("\nChecking for matching books...")
        books = db.get_books_by_query({'embedding': {'$exists': True}}, limit=5)
        
        if not books:
            print("⚠️ No books with embeddings found in database!")
        else:
            print(f"Found {len(books)} books with embeddings for testing.")
            
            # Test similarity with a few books
            for book in books:
                book_vector = book.get('embedding', [])
                if not book_vector:
                    print(f"Book '{book.get('title', 'Unknown')}' has no embedding vector!")
                    continue
                
                similarity = vector_store._cosine_similarity(query_vector, book_vector)
                print(f"Similarity with '{book.get('title', 'Unknown')}': {similarity:.4f} ({round(similarity * 100)}%)")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mood_query = sys.argv[1]
    else:
        mood_query = "adventurous"
    
    debug_query_analysis(mood_query) 