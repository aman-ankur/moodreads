#!/usr/bin/env python3
"""
Mood Vector Recommendations Module
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
        from google_books_emotional_analysis import EmotionalAnalyzer
        
        # Initialize components
        vector_store = VectorEmbeddingStore()
        analyzer = EmotionalAnalyzer()
        
        # Get recommendations from vector store
        recommendations = vector_store.get_recommendations_by_mood(mood_query, limit)
        
        if recommendations:
            logger.info(f"Found {len(recommendations)} vector-based recommendations for mood: {mood_query}")
            return recommendations
        
        # Fallback to text search if no vector recommendations
        logger.info(f"No vector recommendations found, trying text search for mood: {mood_query}")
        
        # Analyze mood query
        mood_analysis = analyzer.analyze_description(f"A book that makes me feel {mood_query}")
        primary_emotions = mood_analysis.get("primary_emotions", [])
        
        # Extract emotion terms for text search
        emotion_terms = " ".join([e["emotion"] for e in primary_emotions])
        
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client.moodreads
        books_collection = db.books
        
        # Search books by emotion terms
        results = list(books_collection.find(
            {"$text": {"$search": emotion_terms}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        
        # Format results
        formatted_results = []
        for book in results:
            formatted_book = {
                "title": book["title"],
                "author": book["author"],
                "cover_url": book.get("cover_url", ""),
                "match_score": int(min(book.get("score", 0) * 20, 100)),  # Convert to percentage
                "matching_emotions": primary_emotions,
                "goodreads_url": book.get("goodreads_url")
            }
            
            # Add emotional profile if available
            if "emotional_profile" in book:
                formatted_book["emotional_arc"] = book["emotional_profile"].get("emotional_arc", {})
                formatted_book["overall_profile"] = book["emotional_profile"].get("overall_emotional_profile", "")
            
            formatted_results.append(formatted_book)
        
        logger.info(f"Found {len(formatted_results)} text-based recommendations for mood: {mood_query}")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error getting mood recommendations: {e}")
        return []

def compare_recommendation_methods(mood_query: str, limit: int = 5) -> Dict:
    """
    Compare vector-based and text-based recommendation methods.
    
    Args:
        mood_query: Mood or emotional state query
        limit: Maximum number of recommendations
        
    Returns:
        Dictionary with results from both methods
    """
    try:
        # Import here to avoid circular imports
        from vector_embeddings import VectorEmbeddingStore
        from google_books_emotional_analysis import EmotionalAnalyzer
        
        # Initialize components
        vector_store = VectorEmbeddingStore()
        analyzer = EmotionalAnalyzer()
        
        # Get vector-based recommendations
        vector_recommendations = vector_store.get_recommendations_by_mood(mood_query, limit)
        
        # Analyze mood query
        mood_analysis = analyzer.analyze_description(f"A book that makes me feel {mood_query}")
        primary_emotions = mood_analysis.get("primary_emotions", [])
        
        # Extract emotion terms for text search
        emotion_terms = " ".join([e["emotion"] for e in primary_emotions])
        
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client.moodreads
        books_collection = db.books
        
        # Get text-based recommendations
        text_results = list(books_collection.find(
            {"$text": {"$search": emotion_terms}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        
        # Format text results
        text_recommendations = []
        for book in text_results:
            formatted_book = {
                "title": book["title"],
                "author": book["author"],
                "cover_url": book.get("cover_url", ""),
                "match_score": int(min(book.get("score", 0) * 20, 100)),  # Convert to percentage
                "matching_emotions": primary_emotions,
                "goodreads_url": book.get("goodreads_url")
            }
            text_recommendations.append(formatted_book)
        
        # Return comparison
        return {
            "mood_query": mood_query,
            "primary_emotions": primary_emotions,
            "vector_recommendations": vector_recommendations,
            "text_recommendations": text_recommendations
        }
        
    except Exception as e:
        logger.error(f"Error comparing recommendation methods: {e}")
        return {
            "mood_query": mood_query,
            "error": str(e),
            "vector_recommendations": [],
            "text_recommendations": []
        }

def main():
    """Main function for testing mood-based vector recommendations."""
    parser = argparse.ArgumentParser(description="Mood Vector Recommendations")
    parser.add_argument("--mood", required=True, help="Mood query for recommendations")
    parser.add_argument("--compare", action="store_true", help="Compare recommendation methods")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of recommendations")
    
    args = parser.parse_args()
    
    if args.compare:
        # Compare recommendation methods
        results = compare_recommendation_methods(args.mood, args.limit)
        
        print(f"\n=== Comparison for Mood: '{args.mood}' ===\n")
        print("Primary Emotions:")
        for emotion in results['primary_emotions']:
            print(f"  - {emotion['emotion']}: {emotion['intensity']}/10")
        
        print("\nVector-based Recommendations:")
        for i, rec in enumerate(results['vector_recommendations']):
            print(f"{i+1}. {rec['title']} by {rec['author']} (Match: {rec['match_score']}%)")
        
        print("\nText-based Recommendations:")
        for i, rec in enumerate(results['text_recommendations']):
            print(f"{i+1}. {rec['title']} by {rec['author']} (Match: {rec['match_score']}%)")
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
            logger.info(f"Saved comparison results to {args.output}")
    else:
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