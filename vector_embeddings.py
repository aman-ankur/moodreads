#!/usr/bin/env python3
"""
Vector Embeddings Module
Generates and stores vector embeddings from emotional analysis for efficient similarity search.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Optional, Union, Tuple
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
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

class VectorEmbeddingStore:
    """Store and retrieve vector embeddings for emotional analysis."""
    
    def __init__(self, mongodb_uri: str = MONGODB_URI, db_name: str = "moodreads"):
        """
        Initialize the vector embedding store.
        
        Args:
            mongodb_uri: MongoDB connection URI
            db_name: Database name
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.books_collection = self.db.books
        self.vectors_collection = self.db.emotion_vectors
        
        # Create indexes
        self._create_indexes()
        
        logger.info("Vector embedding store initialized")
    
    def _create_indexes(self):
        """Create necessary indexes for efficient querying."""
        try:
            # Create index on book_id in vectors collection
            self.vectors_collection.create_index([("book_id", ASCENDING)], unique=True)
            
            # Create index on ISBN in books collection (if it doesn't exist)
            if "isbn_1" not in self.books_collection.index_information():
                self.books_collection.create_index([("isbn", ASCENDING)], 
                                                 unique=True, 
                                                 sparse=True,
                                                 partialFilterExpression={"isbn": {"$type": "string"}})
            
            # Create text index for search
            if "title_text_description_text" not in self.books_collection.index_information():
                self.books_collection.create_index([("title", "text"), ("description", "text")])
            
            logger.info("Indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def generate_emotion_vector(self, emotional_profile: Dict) -> np.ndarray:
        """
        Generate a vector embedding from an emotional profile.
        
        Args:
            emotional_profile: Emotional profile dictionary
            
        Returns:
            Numpy array containing the emotion vector
        """
        # Extract primary emotions and their intensities
        primary_emotions = emotional_profile.get("primary_emotions", [])
        
        # Create a dictionary of emotion intensities
        emotion_dict = {e["emotion"].lower(): e["intensity"] for e in primary_emotions}
        
        # Define standard emotion dimensions for consistent vectors
        standard_emotions = [
            "joy", "sadness", "anger", "fear", "surprise", "disgust", 
            "anticipation", "trust", "wonder", "excitement", "reflection", 
            "tension", "comfort", "outrage", "melancholy", "nostalgia", 
            "hope", "despair", "curiosity", "confusion", "awe", "love",
            "hate", "anxiety", "relief", "pride", "shame", "courage",
            "oppression", "liberation"
        ]
        
        # Create vector with intensity values (0 if emotion not present)
        vector = np.array([emotion_dict.get(emotion, 0.0) for emotion in standard_emotions])
        
        # Normalize vector to unit length if it's not a zero vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def store_emotion_vector(self, book_id: Union[str, ObjectId], emotional_profile: Dict) -> bool:
        """
        Generate and store emotion vector for a book.
        
        Args:
            book_id: MongoDB ID of the book
            emotional_profile: Emotional profile dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(book_id, str):
                book_id = ObjectId(book_id)
            
            # Generate vector
            vector = self.generate_emotion_vector(emotional_profile)
            
            # Store vector in database
            vector_doc = {
                "book_id": book_id,
                "vector": vector.tolist(),
                "dimensions": len(vector),
                "primary_emotions": emotional_profile.get("primary_emotions", []),
                "overall_profile": emotional_profile.get("overall_emotional_profile", "")
            }
            
            # Upsert (update or insert)
            self.vectors_collection.update_one(
                {"book_id": book_id},
                {"$set": vector_doc},
                upsert=True
            )
            
            logger.info(f"Stored emotion vector for book ID: {book_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing emotion vector: {e}")
            return False
    
    def find_similar_books(self, query_vector: np.ndarray, limit: int = 5) -> List[Dict]:
        """
        Find books with similar emotional profiles.
        
        Args:
            query_vector: Query vector to match against
            limit: Maximum number of results to return
            
        Returns:
            List of book dictionaries with similarity scores
        """
        try:
            # Normalize query vector
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                query_vector = query_vector / norm
            
            # Get all vectors from database
            all_vectors = list(self.vectors_collection.find())
            
            # Calculate cosine similarity for each vector
            results = []
            for doc in all_vectors:
                vector = np.array(doc["vector"])
                
                # Calculate cosine similarity
                similarity = np.dot(query_vector, vector)
                
                # Only include results with positive similarity
                if similarity > 0:
                    results.append({
                        "book_id": doc["book_id"],
                        "similarity": float(similarity),
                        "primary_emotions": doc.get("primary_emotions", [])
                    })
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Get book details for top results
            top_results = []
            for result in results[:limit]:
                book = self.books_collection.find_one({"_id": result["book_id"]})
                if book:
                    # Add similarity score and matching emotions
                    book_with_score = {
                        "title": book["title"],
                        "author": book["author"],
                        "cover_url": book.get("cover_url", ""),
                        "match_score": int(result["similarity"] * 100),  # Convert to percentage
                        "matching_emotions": result["primary_emotions"],
                        "goodreads_url": book.get("goodreads_url")
                    }
                    
                    # Add emotional profile if available
                    if "emotional_profile" in book:
                        book_with_score["emotional_arc"] = book["emotional_profile"].get("emotional_arc", {})
                        book_with_score["overall_profile"] = book["emotional_profile"].get("overall_emotional_profile", "")
                    
                    top_results.append(book_with_score)
            
            return top_results
            
        except Exception as e:
            logger.error(f"Error finding similar books: {e}")
            return []
    
    def get_recommendations_by_mood(self, mood_query: str, limit: int = 5) -> List[Dict]:
        """
        Get book recommendations based on a mood query.
        
        Args:
            mood_query: Mood or emotional state query
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended books with similarity scores
        """
        from google_books_emotional_analysis import EmotionalAnalyzer
        
        try:
            # Initialize emotional analyzer
            analyzer = EmotionalAnalyzer()
            
            # Analyze the mood query to extract emotional signals
            mood_analysis = analyzer.analyze_description(
                f"A book that makes me feel {mood_query}"
            )
            
            # Generate vector from mood analysis
            query_vector = self.generate_emotion_vector(mood_analysis)
            
            # Find similar books
            recommendations = self.find_similar_books(query_vector, limit)
            
            logger.info(f"Found {len(recommendations)} recommendations for mood: {mood_query}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations by mood: {e}")
            return []
    
    def process_book_for_vectors(self, book: Dict) -> bool:
        """
        Process a book to generate and store its emotion vector.
        
        Args:
            book: Book dictionary with emotional profile
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if book has an emotional profile
            if "emotional_profile" not in book:
                logger.warning(f"Book '{book.get('title', 'Unknown')}' has no emotional profile")
                return False
            
            # Get book ID
            book_id = book.get("_id")
            if not book_id:
                logger.warning(f"Book '{book.get('title', 'Unknown')}' has no ID")
                return False
            
            # Store emotion vector
            return self.store_emotion_vector(book_id, book["emotional_profile"])
            
        except Exception as e:
            logger.error(f"Error processing book for vectors: {e}")
            return False

def main():
    """Main function for testing the vector embedding store."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector Embedding Store")
    parser.add_argument("--mood", help="Mood query for recommendations")
    parser.add_argument("--book-id", help="Process a specific book by ID")
    parser.add_argument("--process-all", action="store_true", help="Process all books in database")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of recommendations")
    
    args = parser.parse_args()
    
    vector_store = VectorEmbeddingStore()
    
    if args.mood:
        # Get recommendations by mood
        recommendations = vector_store.get_recommendations_by_mood(args.mood, args.limit)
        
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
    
    elif args.book_id:
        # Process a specific book
        book = vector_store.books_collection.find_one({"_id": ObjectId(args.book_id)})
        if book:
            success = vector_store.process_book_for_vectors(book)
            print(f"Processed book '{book['title']}': {'Success' if success else 'Failed'}")
    
    elif args.process_all:
        # Process all books in database
        books = vector_store.books_collection.find({"emotional_profile": {"$exists": True}})
        count = 0
        success_count = 0
        
        for book in books:
            count += 1
            if vector_store.process_book_for_vectors(book):
                success_count += 1
        
        print(f"Processed {count} books, {success_count} successful")

if __name__ == "__main__":
    main() 