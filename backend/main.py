from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from decouple import config
import logging
import traceback

from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.recommender.engine import RecommendationEngine
from moodreads.database.mongodb import MongoDBClient

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
analyzer = EmotionalAnalyzer(use_cache=True)
recommender = RecommendationEngine()
db = MongoDBClient()

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

@app.post("/api/recommendations", response_model=List[Book])
async def get_recommendations(request: MoodRequest):
    """Get book recommendations based on mood."""
    try:
        # Use query if provided, otherwise use mood
        query_text = request.query or request.mood
        
        # Analyze the emotional query
        try:
            emotional_profile, _ = analyzer.analyze(request.mood)
        except Exception as e:
            logging.error(f"Emotional analysis failed: {str(e)}")
            # Use default emotional profile as fallback
            emotional_profile = {
                'joy': 0.5,
                'sadness': 0.5,
                'tension': 0.5,
                'comfort': 0.5,
                'inspiration': 0.5,
                'melancholy': 0.5,
                'hope': 0.5
            }
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            emotional_profile=emotional_profile,
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
        logging.error(f"Recommendation error: {str(e)}")
        logging.error(f"Request data: {request.dict()}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recommendations. Please try again."
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 