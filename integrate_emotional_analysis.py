#!/usr/bin/env python3
"""
Integration Module for Enhanced Emotional Analysis
Combines the enhanced Goodreads scraper with emotional analysis and vector embeddings.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Import custom modules
from enhanced_goodreads_scraper import EnhancedGoodreadsScraper
from google_books_emotional_analysis import EmotionalAnalyzer
from vector_embeddings import VectorEmbeddingStore, MongoJSONEncoder

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/moodreads")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BookDataIntegrator:
    """
    Integrates book data from various sources and provides mood-based recommendations.
    This class serves as the main integration point for the MoodReads application.
    """
    
    def __init__(self, mongodb_uri: str = MONGODB_URI, db_name: str = "moodreads"):
        """Initialize the book data integrator."""
        # Initialize MongoDB connection
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.books_collection = self.db.books
        
        # Initialize components
        self.scraper = EnhancedGoodreadsScraper()
        self.emotional_analyzer = EmotionalAnalyzer()
        self.vector_store = VectorEmbeddingStore(mongodb_uri, db_name)
        
        logger.info("BookDataIntegrator initialized")
    
    def process_book(self, query: str) -> Optional[Dict]:
        """
        Process a book by query (title/author), integrating data from Goodreads and Google Books.
        
        Args:
            query: Book title or author query
            
        Returns:
            Integrated book data with emotional profile
        """
        try:
            # Search for book on Goodreads
            logger.info(f"Searching for book: {query}")
            book_data = self.scraper.process_book(query)
            
            if not book_data:
                logger.warning(f"Book not found on Goodreads: {query}")
                return None
            
            # Add emotional profile
            logger.info(f"Creating emotional profile for: {book_data['title']}")
            
            # Extract description and reviews for analysis
            description = book_data.get('description', '')
            reviews = book_data.get('reviews', [])
            
            # Create emotional profile
            emotional_profile = self.emotional_analyzer.create_emotional_profile({
                'title': book_data['title'],
                'description': description,
                'reviews': reviews,
                'categories': book_data.get('genres', [])
            })
            
            # Add emotional profile to book data
            book_data['emotional_profile'] = emotional_profile
            
            # Store in MongoDB
            self._store_book(book_data)
            
            # Process for vector embeddings
            self.vector_store.process_book_for_vectors(book_data)
            
            logger.info(f"Successfully processed book: {book_data['title']}")
            return book_data
            
        except Exception as e:
            logger.error(f"Error processing book: {e}")
            return None
    
    def get_mood_recommendations(self, mood_query: str, limit: int = 5) -> List[Dict]:
        """
        Get book recommendations based on a mood query.
        
        Args:
            mood_query: Mood or emotional state query
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended books with similarity scores
        """
        try:
            # Get recommendations from vector store
            recommendations = self.vector_store.get_recommendations_by_mood(mood_query, limit)
            
            if recommendations:
                logger.info(f"Found {len(recommendations)} vector-based recommendations for mood: {mood_query}")
                return recommendations
            
            # Fallback to text search if no vector recommendations
            logger.info(f"No vector recommendations found, trying text search for mood: {mood_query}")
            
            # Analyze mood query
            mood_analysis = self.emotional_analyzer.analyze_description(f"A book that makes me feel {mood_query}")
            primary_emotions = mood_analysis.get("primary_emotions", [])
            
            # Extract emotion terms for text search
            emotion_terms = " ".join([e["emotion"] for e in primary_emotions])
            
            # Search books by emotion terms
            results = list(self.books_collection.find(
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
    
    def _store_book(self, book_data: Dict) -> bool:
        """
        Store book data in MongoDB.
        
        Args:
            book_data: Book data to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if book already exists
            existing_book = self.books_collection.find_one({"title": book_data["title"], "author": book_data["author"]})
            
            if existing_book:
                # Update existing book
                book_data["_id"] = existing_book["_id"]
                book_data["last_updated"] = datetime.now()
                
                self.books_collection.replace_one({"_id": existing_book["_id"]}, book_data)
                logger.info(f"Updated existing book: {book_data['title']}")
            else:
                # Insert new book
                book_data["created_at"] = datetime.now()
                book_data["last_updated"] = datetime.now()
                
                result = self.books_collection.insert_one(book_data)
                book_data["_id"] = result.inserted_id
                logger.info(f"Inserted new book: {book_data['title']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing book: {e}")
            return False

class EmotionalRecommendationSystem:
    """
    Integrates Goodreads scraping, emotional analysis, and vector embeddings
    to provide enhanced book recommendations based on emotional content.
    """
    
    def __init__(self, mongodb_uri: str = MONGODB_URI, db_name: str = "moodreads"):
        """Initialize the emotional recommendation system."""
        # Initialize MongoDB connection
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.books_collection = self.db.books
        
        # Initialize components
        self.scraper = EnhancedGoodreadsScraper()
        self.analyzer = EmotionalAnalyzer()
        self.vector_store = VectorEmbeddingStore(mongodb_uri, db_name)
        
        logger.info("Emotional recommendation system initialized")
    
    def get_advanced_mood_recommendations(self, mood_query: str, limit: int = 5) -> List[Dict]:
        """
        Get book recommendations based on a mood query using vector similarity.
        
        Args:
            mood_query: Mood or emotional state query
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended books with similarity scores
        """
        try:
            # Get recommendations from vector store
            recommendations = self.vector_store.get_recommendations_by_mood(mood_query, limit)
            
            if recommendations:
                logger.info(f"Found {len(recommendations)} vector-based recommendations for mood: {mood_query}")
                return recommendations
            
            # Fallback to text search if no vector recommendations
            logger.info(f"No vector recommendations found, trying text search for mood: {mood_query}")
            
            # Analyze mood query
            mood_analysis = self.analyzer.analyze_description(f"A book that makes me feel {mood_query}")
            primary_emotions = mood_analysis.get("primary_emotions", [])
            
            # Extract emotion terms for text search
            emotion_terms = " ".join([e["emotion"] for e in primary_emotions])
            
            # Search books by emotion terms
            results = list(self.books_collection.find(
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
            logger.error(f"Error getting advanced mood recommendations: {e}")
            return []

def main():
    """Main function for testing the emotional recommendation system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Emotional Recommendation System")
    parser.add_argument("--mood", help="Mood query for recommendations")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    
    args = parser.parse_args()
    
    system = EmotionalRecommendationSystem()
    
    if args.mood:
        # Get advanced recommendations
        recommendations = system.get_advanced_mood_recommendations(args.mood, args.limit)
        
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

if __name__ == "__main__":
    main() 