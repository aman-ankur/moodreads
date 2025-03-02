from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import random
import logging
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
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

# Mock data for recommendations
SAMPLE_BOOKS = [
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "isbn": "9780061120084",
        "url": "https://openlibrary.org/books/OL22172199M"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "9780451524935",
        "url": "https://openlibrary.org/books/OL7360734M"
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "url": "https://openlibrary.org/books/OL7318592M"
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "isbn": "9780141439518",
        "url": "https://openlibrary.org/books/OL8327968M"
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "9780316769488",
        "url": "https://openlibrary.org/books/OL7361409M"
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "isbn": "9780060850524",
        "url": "https://openlibrary.org/books/OL7941080M"
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "9780618260300",
        "url": "https://openlibrary.org/books/OL7318408M"
    }
]

class Book(BaseModel):
    id: int
    title: str
    author: str
    coverUrl: str
    emotionalMatch: float
    matchExplanation: str

class MoodRequest(BaseModel):
    mood: str
    query: str = None  # Optional query field, defaults to mood if not provided

def transform_book_data(book: dict, score: float) -> Book:
    """Transform raw book data into the frontend format."""
    return Book(
        id=hash(book.get("url", "")),  # Use URL hash as ID
        title=book.get("title", "Unknown"),
        author=book.get("author", "Unknown"),
        coverUrl=f"https://covers.openlibrary.org/b/isbn/{book.get('isbn', '0')}-L.jpg",
        emotionalMatch=score * 100,  # Convert to percentage
        matchExplanation=f"This book matches your emotional state with a {score:.0%} confidence level."
    )

def get_mock_recommendations(mood: str, query: str = None, limit: int = 5):
    """Generate mock recommendations based on mood and query."""
    # Shuffle the sample books to simulate different recommendations
    books = SAMPLE_BOOKS.copy()
    random.shuffle(books)
    
    # Generate random scores between 0.7 and 0.95
    scores = [random.uniform(0.7, 0.95) for _ in range(len(books))]
    
    # Sort by score in descending order
    recommendations = sorted(zip(books, scores), key=lambda x: x[1], reverse=True)
    
    # Return the top N recommendations
    return recommendations[:limit]

@app.post("/api/recommendations", response_model=List[Book])
async def get_recommendations(request: MoodRequest):
    """Get book recommendations based on mood."""
    try:
        # Use query if provided, otherwise use mood
        query_text = request.query or request.mood
        
        logger.info(f"Received recommendation request for mood: {request.mood}, query: {query_text}")
        
        # Get mock recommendations
        recommendations = get_mock_recommendations(
            mood=request.mood,
            query=query_text,
            limit=5
        )
        
        if not recommendations:
            return []
        
        # Transform recommendations into frontend format
        return [
            transform_book_data(book, score)
            for book, score in recommendations
        ]
        
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        logger.error(f"Request data: {request.dict()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recommendations. Please try again."
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 