#!/usr/bin/env python3
"""
Test API for Vector-Based Recommendations
A FastAPI application to test the vector-based recommendation system.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MoodReads Advanced Recommendations API",
    description="API for testing vector-based emotional book recommendations",
    version="0.1.0"
)

# Enable CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request and response models
class MoodRequest(BaseModel):
    mood: str = Field(..., description="Mood or emotional state query")
    limit: int = Field(5, description="Maximum number of recommendations")

class EmotionData(BaseModel):
    emotion: str = Field(..., description="Emotion name")
    intensity: float = Field(..., description="Emotion intensity (0-10)")

class EmotionalArc(BaseModel):
    beginning: Optional[List[EmotionData]] = Field(None, description="Emotions at the beginning")
    middle: Optional[List[EmotionData]] = Field(None, description="Emotions in the middle")
    end: Optional[List[EmotionData]] = Field(None, description="Emotions at the end")

class BookRecommendation(BaseModel):
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    cover_url: Optional[str] = Field(None, description="URL to book cover image")
    match_score: int = Field(..., description="Match score as percentage")
    matching_emotions: List[EmotionData] = Field(..., description="Matching emotions")
    emotional_arc: Optional[EmotionalArc] = Field(None, description="Emotional arc of the book")
    overall_profile: Optional[str] = Field(None, description="Overall emotional profile")
    goodreads_url: Optional[str] = Field(None, description="Goodreads URL")

# JSON encoder for MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

@app.post("/api/advanced-recommendations", response_model=List[BookRecommendation])
async def get_advanced_recommendations(request: MoodRequest):
    """
    Get book recommendations based on a mood query using vector similarity.
    """
    try:
        logger.info(f"Received mood request: {request.mood}, limit: {request.limit}")
        
        # Import here to avoid circular imports
        from vector_embeddings import VectorEmbeddingStore
        
        # Get recommendations
        vector_store = VectorEmbeddingStore()
        recommendations = vector_store.get_recommendations_by_mood(request.mood, request.limit)
        
        if not recommendations:
            logger.warning(f"No recommendations found for mood: {request.mood}")
            return []
        
        logger.info(f"Returning {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        # Import to check if modules are available
        from vector_embeddings import VectorEmbeddingStore
        from google_books_emotional_analysis import EmotionalAnalyzer
        
        return {
            "status": "healthy",
            "message": "API is running correctly",
            "components": {
                "vector_embeddings": "available",
                "emotional_analyzer": "available"
            }
        }
    except ImportError as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Missing component: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
        }

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "MoodReads Advanced Recommendations API",
        "version": "0.1.0",
        "description": "API for testing vector-based emotional book recommendations",
        "endpoints": {
            "/api/advanced-recommendations": "Get book recommendations based on mood",
            "/api/health": "Health check endpoint"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 