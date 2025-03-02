"""
Integration tests for the recommendation API.
"""

import pytest
from fastapi.testclient import TestClient
import json
from typing import Dict, Any
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.append(project_root)

from backend.main import app
from moodreads.database.mongodb import MongoDBClient

client = TestClient(app)

@pytest.fixture
def db():
    """Database fixture."""
    return MongoDBClient()

@pytest.fixture
def sample_book() -> Dict[str, Any]:
    """Sample book with emotional profile."""
    return {
        'title': 'Test Book',
        'author': 'Test Author',
        'description': 'A test book about joy and wonder',
        'emotional_profile': {
            'primary_emotions': [
                {'emotion': 'joy', 'intensity': 8},
                {'emotion': 'wonder', 'intensity': 7}
            ]
        },
        'embeddings': [0.8, 0.7, 0.0, 0.0, 0.0],  # Simple test vector
        'rating': 4.5,
        'genres': ['Fiction', 'Fantasy']
    }

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['recommender'] == 'initialized'
    assert data['database'] == 'connected'

def test_recommendations_empty_query():
    """Test recommendations with empty query."""
    response = client.post("/api/recommendations", json={'mood': ''})
    assert response.status_code == 200
    assert response.json() == []

def test_recommendations_basic_query():
    """Test recommendations with a basic mood query."""
    response = client.post("/api/recommendations", 
                          json={'mood': 'I want a happy and uplifting book'})
    assert response.status_code == 200
    recommendations = response.json()
    
    # Check response structure
    if recommendations:  # If we got any recommendations
        book = recommendations[0]
        assert 'id' in book
        assert 'title' in book
        assert 'author' in book
        assert 'coverUrl' in book
        assert 'emotionalMatch' in book
        assert isinstance(book['emotionalMatch'], float)
        assert 0 <= book['emotionalMatch'] <= 100

def test_recommendations_with_sample_book(db, sample_book):
    """Test recommendations with a sample book in the database."""
    # Insert sample book
    book_id = db.books_collection.insert_one(sample_book).inserted_id
    
    try:
        # Test recommendation
        response = client.post("/api/recommendations", 
                             json={'mood': 'I want a joyful and wonderful book'})
        assert response.status_code == 200
        recommendations = response.json()
        
        # We should get at least one recommendation (our sample book)
        assert len(recommendations) > 0
        
        # Check if our sample book is in the recommendations
        book_ids = [book['id'] for book in recommendations]
        assert str(book_id) in book_ids
        
        # Check emotional match score
        sample_rec = next(r for r in recommendations if r['id'] == str(book_id))
        assert sample_rec['emotionalMatch'] > 0
        
    finally:
        # Clean up
        db.books_collection.delete_one({'_id': book_id})

def test_recommendations_with_query_parameter():
    """Test recommendations using the optional query parameter."""
    response = client.post("/api/recommendations", 
                          json={'mood': 'happy', 'query': 'I want a book that will make me laugh'})
    assert response.status_code == 200
    recommendations = response.json()
    
    # The API should use the query field instead of mood
    # We can't test the exact recommendations, but we can verify the structure
    if recommendations:
        book = recommendations[0]
        assert all(key in book for key in ['id', 'title', 'author', 'coverUrl', 'emotionalMatch'])

def test_recommendations_error_handling():
    """Test error handling in recommendations endpoint."""
    # Test with invalid JSON
    response = client.post("/api/recommendations", 
                          data="invalid json")
    assert response.status_code == 422  # FastAPI validation error
    
    # Test with missing required field
    response = client.post("/api/recommendations", 
                          json={'query': 'missing mood field'})
    assert response.status_code == 422  # FastAPI validation error
    
    # Test with invalid mood type
    response = client.post("/api/recommendations", 
                          json={'mood': 123})  # mood should be string
    assert response.status_code == 422  # FastAPI validation error 