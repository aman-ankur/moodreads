import sys
import os
from pathlib import Path
import urllib.parse

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import traceback

# Import the recommendation system
from moodreads.recommendation.enhanced_recommender import EnhancedRecommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change from DEBUG to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the recommender
recommender = EnhancedRecommender()

class Book(BaseModel):
    id: str  # Changed from int to str since MongoDB uses string IDs
    title: str
    author: str
    coverUrl: str
    emotionalMatch: float
    matchExplanation: str
    genres: Optional[List[str]] = None
    rating: Optional[float] = None

class MoodRequest(BaseModel):
    mood: str
    query: Optional[str] = None  # Optional query field, defaults to mood if not provided

def transform_book_data(book: dict, score: float) -> Book:
    """Transform book data from database format to API response format."""
    # Convert match score to percentage (rounded to 1 decimal place)
    display_match = round(min(score * 100 + 50, 100.0), 1)
    
    # Determine cover URL with better fallbacks
    cover_url = ""
    cover_source = "none"
    
    # Try to get OpenLibrary cover first
    isbn = book.get('isbn', '')
    if isbn:
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
        cover_source = "openlibrary"
    
    # If no ISBN or we want to use Google Books as primary source
    if not cover_url or not isbn:
        # Check for Google thumbnail
        if book.get('google_thumbnail', ''):
            cover_url = book.get('google_thumbnail', '')
            cover_source = "google_thumbnail"
        # Check for cover_image field
        elif book.get('cover_image', ''):
            cover_url = book.get('cover_image', '')
            cover_source = "cover_image"
        # If still no image, try a Google Books search with the title and author
        else:
            title = book.get('title', '')
            author = book.get('author', '')
            if title and author and title != "Unknown Title":
                # Use a reliable placeholder with the book title encoded
                encoded_title = urllib.parse.quote(title)
                encoded_author = urllib.parse.quote(author)
                cover_url = f"https://books.google.com/books/content?id=_&printsec=frontcover&img=1&zoom=1&q={encoded_title}+{encoded_author}"
                cover_source = "google_books_search"
    
    # Last resort fallback
    if not cover_url or cover_url == "":
        cover_url = "https://via.placeholder.com/300x450?text=No+Cover+Available"
        cover_source = "placeholder"
    
    logger.info(f"Transforming book: {book.get('title', 'Unknown')} with match score: {score}, display match: {display_match}, cover source: {cover_source}")
    
    # Create Book object
    return Book(
        id=str(book.get('_id', '')),
        title=book.get('title', 'Unknown Title'),
        author=book.get('author', 'Unknown Author'),
        coverUrl=cover_url,
        emotionalMatch=display_match,
        matchExplanation=book.get('explanation', 'This book matches your emotional preferences.'),
        genres=book.get('genres', []),
        rating=book.get('rating', 0.0)
    )

@app.post("/api/recommendations", response_model=List[Book])
async def get_recommendations(request: MoodRequest):
    """Get book recommendations based on mood."""
    try:
        # Use query if provided, otherwise use mood
        query_text = request.query or request.mood
        
        logger.info(f"Received recommendation request for mood: {request.mood}, query: {query_text}")
        
        # Get recommendations using the enhanced recommender
        logger.info("Calling recommender.recommend_books...")
        recommendations = recommender.recommend_books(
            query=query_text,
            limit=20  # Increase limit to get more potential matches
        )
        
        logger.info(f"Got {len(recommendations)} recommendations from recommender")
        
        if not recommendations:
            logger.warning("No recommendations found")
            return []
        
        # Log the first recommendation for debugging
        if recommendations and len(recommendations) > 0:
            first_rec = recommendations[0]
            logger.info(f"First recommendation before transformation: {first_rec.get('title', 'Unknown')}")
            logger.info(f"Fields in first recommendation: {list(first_rec.keys())}")
            logger.info(f"Match score: {first_rec.get('match_score', 0)}")
            
            # Additional logging to check for score issues
            for i, rec in enumerate(recommendations[:5]):
                logger.info(f"Recommendation {i+1}: {rec.get('title', 'Unknown')} - Match score: {rec.get('match_score', 0)}")
                # Also log the book ID for cross-referencing
                logger.info(f"  - ID: {rec.get('_id', 'Unknown')}")
        
        # Store original recommendations for potential fallback
        original_recommendations = recommendations.copy()
        original_count = len(original_recommendations)
        
        # Count books with various match scores
        good_matches = [book for book in recommendations if float(book.get('match_score', 0)) > 0.03]
        small_matches = [book for book in recommendations if 0.001 < float(book.get('match_score', 0)) <= 0.03]
        zero_matches = [book for book in recommendations if float(book.get('match_score', 0)) <= 0.001]
        
        logger.info(f"Score breakdown: {len(good_matches)} good matches, {len(small_matches)} small matches, {len(zero_matches)} zero matches")
        
        # Check for and log any books with problematic titles
        for book in good_matches:
            title = book.get('title', '')
            book_id = book.get('_id', 'No ID')
            if not title or title.lower() == 'unknown' or title.lower() == 'unknown title':
                logger.warning(f"Found book with missing/unknown title: ID={book_id}")
                logger.warning(f"Full book data for debugging: {book}")
                # Special debug for the problematic book we've identified
                if str(book_id) == '67c36080e10fd8eb774c2fdf':
                    logger.warning(f"DETAILED DEBUG - Found the problematic 'Unknown Title' book with ID 67c36080e10fd8eb774c2fdf")
                    logger.warning(f"Book fields: {list(book.keys())}")
                    for key, value in book.items():
                        if key != 'description' and key != 'explanation':  # Skip long text fields
                            logger.warning(f"  - {key}: {value}")
        
        # Filter out books with missing or "Unknown" titles
        def has_valid_title(book):
            title = book.get('title', '').strip()
            return title and title.lower() != 'unknown' and title.lower() != 'unknown title'
        
        good_matches_before = len(good_matches)
        good_matches = [book for book in good_matches if has_valid_title(book)]
        if good_matches_before > len(good_matches):
            logger.warning(f"Removed {good_matches_before - len(good_matches)} books with invalid titles from good matches")
            
        small_matches = [book for book in small_matches if has_valid_title(book)]
        zero_matches = [book for book in zero_matches if has_valid_title(book)]
        
        logger.info(f"After title filtering: {len(good_matches)} good matches, {len(small_matches)} small matches, {len(zero_matches)} zero matches")
        
        # If we have good matches, prioritize those
        if good_matches:
            logger.info(f"Found {len(good_matches)} good matches with scores > 0.03")
            recommendations = good_matches
            logger.info(f"Using good matches: {', '.join([b.get('title', 'Unknown') for b in recommendations[:3]])}")
        # Otherwise, if we have small non-zero matches, use those
        elif small_matches:
            logger.info(f"Using {len(small_matches)} books with small non-zero match scores")
            recommendations = small_matches
            logger.info(f"Using small matches: {', '.join([b.get('title', 'Unknown') for b in recommendations[:3]])}")
        # If all else fails, fall back to original recommendations (which might all be 0)
        else:
            logger.warning("No recommendations with non-zero match scores")
            if original_count > 0:
                logger.warning("Using top 5 recommendations regardless of match score")
                recommendations = original_recommendations[:5]
                logger.info(f"Using fallback recommendations: {', '.join([b.get('title', 'Unknown') for b in recommendations[:3]])}")
            else:
                return []
        
        # Ensure we don't return more than 10 books
        if len(recommendations) > 10:
            logger.info(f"Limiting from {len(recommendations)} to 10 recommendations")
            recommendations = recommendations[:10]
        
        # Transform recommendations into frontend format
        logger.info("Transforming recommendations...")
        transformed_recommendations = []
        
        for book in recommendations:
            try:
                # Extract raw match score
                match_score = float(book.get('match_score', 0))
                
                # Create transformed book
                transformed_book = transform_book_data(book, match_score)
                transformed_recommendations.append(transformed_book)
                
                logger.info(f"Transformed: {book.get('title', 'Unknown')} with score {match_score} to display match: {transformed_book.emotionalMatch}%")
            except Exception as e:
                logger.error(f"Error transforming book {book.get('title', 'Unknown')}: {str(e)}")
                # Continue with next book
        
        logger.info(f"Returning {len(transformed_recommendations)} transformed recommendations")
        
        # Log the first few transformed recommendations
        for i, book in enumerate(transformed_recommendations[:3]):
            logger.info(f"Transformed recommendation {i+1}: {book.title} - Match: {book.emotionalMatch}%")
            
        return transformed_recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        return []

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if recommender is initialized and can connect to MongoDB
        recommender.db.ping()
        return {
            "status": "healthy",
            "recommender": "initialized",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service unhealthy"
        )

def _find_closest_emotion(self, emotion: str) -> str:
    """Find the closest primary emotion to the given emotion."""
    # Use the enhanced implementation from vector_embeddings.py
    try:
        from moodreads.analysis.vector_embeddings import VectorEmbeddingStore
        
        # Initialize the vector store if not already initialized
        if not hasattr(self, 'vector_store'):
            self.vector_store = VectorEmbeddingStore()
            logger.info("Vector embedding store initialized for emotion mapping")
        
        # Use the enhanced emotion mapping from the vector store
        closest_emotion = self.vector_store._find_closest_emotion(emotion)
        logger.info(f"Using enhanced emotion mapping: '{emotion}' -> '{closest_emotion}'")
        
        # Update our local mappings
        self.emotion_mappings[emotion] = closest_emotion
        self._save_emotion_mappings()  # Optional: only save occasionally to avoid too many writes
        
        return closest_emotion
    except ImportError:
        logger.warning("VectorEmbeddingStore not available, falling back to basic mapping")
        # Fall back to the existing implementation
        
        # First check if we have a direct mapping
        if emotion in self.emotion_mappings:
            return self.emotion_mappings[emotion]
            
        # Add these common mappings that are currently defaulting to wonder
        common_mappings = {
            "wisdom": "curiosity",       # Instead of wonder
            "wise": "curiosity",         # Instead of wonder
            "understanding": "empathy",  # Instead of wonder
            "reflection": "contemplation", # Instead of wonder
            "knowledge": "curiosity",    # This one is already mapped correctly
            "insight": "contemplation",
            "philosophical": "contemplation",
            "thoughtful": "empathy",
            "enlightenment": "awe",
            "learning": "curiosity"
        }
        
        if emotion in common_mappings:
            # Add this mapping to our database for future use
            self.emotion_mappings[emotion] = common_mappings[emotion]
            self._save_emotion_mappings()
            logger.info(f"Added new mapping: '{emotion}' -> '{common_mappings[emotion]}'")
            return common_mappings[emotion]
            
        # Existing Claude API call and fallback logic... 