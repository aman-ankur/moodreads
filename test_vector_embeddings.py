#!/usr/bin/env python3
"""
Test script for the vector embeddings module.
"""

import os
import json
import logging
import argparse
import numpy as np
from typing import Dict, List
from bson import ObjectId

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MongoJSONEncoder(json.JSONEncoder):
    """JSON encoder that can handle MongoDB ObjectId."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def test_vector_generation(emotional_profile: Dict) -> np.ndarray:
    """
    Test generating a vector from an emotional profile.
    
    Args:
        emotional_profile: Emotional profile dictionary
        
    Returns:
        Generated vector
    """
    from vector_embeddings import VectorEmbeddingStore
    
    vector_store = VectorEmbeddingStore()
    vector = vector_store.generate_emotion_vector(emotional_profile)
    
    logger.info(f"Generated vector with {len(vector)} dimensions")
    logger.info(f"Vector norm: {np.linalg.norm(vector)}")
    
    return vector

def test_mood_recommendations(mood_query: str, limit: int = 5) -> List[Dict]:
    """
    Test getting recommendations by mood.
    
    Args:
        mood_query: Mood query
        limit: Maximum number of recommendations
        
    Returns:
        List of recommendations
    """
    from vector_embeddings import VectorEmbeddingStore
    
    vector_store = VectorEmbeddingStore()
    recommendations = vector_store.get_recommendations_by_mood(mood_query, limit)
    
    logger.info(f"Found {len(recommendations)} recommendations for mood: {mood_query}")
    
    return recommendations

def test_process_book(book_id: str) -> bool:
    """
    Test processing a book for vector embeddings.
    
    Args:
        book_id: MongoDB ID of the book
        
    Returns:
        True if successful, False otherwise
    """
    from vector_embeddings import VectorEmbeddingStore
    from pymongo import MongoClient
    
    vector_store = VectorEmbeddingStore()
    
    # Get book from database
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/moodreads"))
    db = client.moodreads
    book = db.books.find_one({"_id": ObjectId(book_id)})
    
    if not book:
        logger.error(f"Book not found with ID: {book_id}")
        return False
    
    # Process book
    success = vector_store.process_book_for_vectors(book)
    
    logger.info(f"Processed book '{book['title']}': {'Success' if success else 'Failed'}")
    
    return success

def main():
    """Main function for testing vector embeddings."""
    parser = argparse.ArgumentParser(description="Test Vector Embeddings")
    parser.add_argument("--mood", help="Mood query for recommendations")
    parser.add_argument("--book-id", help="Process a specific book by ID")
    parser.add_argument("--process-all", action="store_true", help="Process all books in database")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of recommendations")
    
    args = parser.parse_args()
    
    if args.mood:
        # Test mood recommendations
        recommendations = test_mood_recommendations(args.mood, args.limit)
        
        if recommendations:
            print(f"\n=== Book Recommendations for Mood: '{args.mood}' ===\n")
            for i, rec in enumerate(recommendations):
                print(f"{i+1}. {rec['title']} by {rec['author']}")
                print(f"   Match Score: {rec['match_score']}%")
                print(f"   Matching Emotions:")
                for emotion in rec['matching_emotions']:
                    print(f"     - {emotion['emotion']}: {emotion['intensity']}/10")
                print()
            
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(recommendations, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
                logger.info(f"Saved recommendations to {args.output}")
        else:
            print(f"No recommendations found for mood: '{args.mood}'")
    
    elif args.book_id:
        # Test processing a book
        success = test_process_book(args.book_id)
        print(f"Book processing {'successful' if success else 'failed'}")
    
    elif args.process_all:
        # Test processing all books
        from vector_embeddings import VectorEmbeddingStore
        from pymongo import MongoClient
        
        vector_store = VectorEmbeddingStore()
        
        # Get all books with emotional profiles
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/moodreads"))
        db = client.moodreads
        books = db.books.find({"emotional_profile": {"$exists": True}})
        
        count = 0
        success_count = 0
        
        for book in books:
            count += 1
            if vector_store.process_book_for_vectors(book):
                success_count += 1
        
        print(f"Processed {count} books, {success_count} successful")
    
    else:
        # Test with a sample emotional profile
        sample_profile = {
            "primary_emotions": [
                {"emotion": "Wonder", "intensity": 9.0},
                {"emotion": "Excitement", "intensity": 8.0},
                {"emotion": "Joy", "intensity": 7.5},
                {"emotion": "Anticipation", "intensity": 7.0}
            ],
            "overall_emotional_profile": "A sense of wonder and excitement"
        }
        
        vector = test_vector_generation(sample_profile)
        print(f"Sample vector: {vector[:5]}... (showing first 5 dimensions)")

if __name__ == "__main__":
    main() 