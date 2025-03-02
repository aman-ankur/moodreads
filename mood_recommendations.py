#!/usr/bin/env python3
"""
Mood Recommendations Module
Provides mood-based book recommendations using vector embeddings.
"""

import os
import json
import logging
import argparse
from typing import List, Dict
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/moodreads")

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
        return super().default(obj)

def get_mood_recommendations(mood_query: str, limit: int = 5) -> List[Dict]:
    """
    Get book recommendations based on a mood query.
    
    Args:
        mood_query: Mood or emotional state query
        limit: Maximum number of recommendations
        
    Returns:
        List of recommended books with similarity scores
    """
    try:
        # Import here to avoid circular imports
        from vector_embeddings import VectorEmbeddingStore
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore()
        
        # Get recommendations from vector store
        recommendations = vector_store.get_recommendations_by_mood(mood_query, limit)
        
        logger.info(f"Found {len(recommendations)} recommendations for mood: {mood_query}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting mood recommendations: {e}")
        return []

def main():
    """Main function for testing mood-based recommendations."""
    parser = argparse.ArgumentParser(description="Mood Recommendations")
    parser.add_argument("--mood", required=True, help="Mood query for recommendations")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of recommendations")
    
    args = parser.parse_args()
    
    # Get recommendations by mood
    recommendations = get_mood_recommendations(args.mood, args.limit)
    
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

if __name__ == "__main__":
    main() 