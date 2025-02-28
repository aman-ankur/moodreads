import pytest
from moodreads.recommender.engine import RecommendationEngine
from app.pages.recommendations import transform_book_data

def test_recommendation_engine_initialization():
    engine = RecommendationEngine()
    assert engine is not None

def test_get_recommendations():
    engine = RecommendationEngine()
    emotional_profile = {
        "joy": 0.8,
        "comfort": 0.7,
        "inspiration": 0.9
    }
    user_text = "I want an uplifting book about personal growth"
    
    recommendations = engine.get_recommendations(emotional_profile, user_text)
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5  # Default limit

def test_transform_book_data_basic():
    """Test basic book data transformation"""
    input_data = {
        "title": "Test Book",
        "author": "Test Author",
        "rating": 4.5,
        "year": "2023",
        "isbn": "1234567890",
        "url": "https://example.com",
        "description": "A test book",
        "genres": ["Fiction", "Drama"]
    }
    
    result = transform_book_data(input_data)
    
    assert result["title"] == "Test Book"
    assert result["author"] == "Test Author"
    assert result["rating"] == "4.50"
    assert result["year"] == "2023"
    assert result["isbn"] == "1234567890"
    assert result["url"] == "https://example.com"
    assert result["description"] == "A test book"
    assert result["genres"] == ["Fiction", "Drama"]

def test_transform_book_data_edge_cases():
    """Test edge cases in book data transformation"""
    input_data = {
        "title": "<script>alert('xss')</script>Bad Title",
        "author": None,
        "rating": "not a number",
        "year": "",
        "isbn": None,
        "url": "",
        "description": "From Goodreads: Some description",
        "genres": "Fiction,Drama"
    }
    
    result = transform_book_data(input_data)
    
    assert "<script>" not in result["title"]
    assert result["author"] == "Unknown Author"
    assert result["rating"] == ""  # Invalid rating should return empty string
    assert result["year"] == ""
    assert result["isbn"] == "0"
    assert result["url"] == ""
    assert result["description"] == "Some description"  # Prefix should be removed
    assert isinstance(result["genres"], list)
    assert len(result["genres"]) == 2

def test_transform_book_data_description_cleaning():
    """Test description cleaning logic"""
    test_cases = [
        {
            "input": "From Goodreads: A great book",
            "expected": "A great book"
        },
        {
            "input": "Book description: Another book",
            "expected": "Another book"
        },
        {
            "input": "A book about readers. The story continues",
            "expected": "The story continues"
        },
        {
            "input": "<p>HTML content</p>",
            "expected": "<p>HTML content</p>"  # HTML should be preserved for proper escaping
        }
    ]
    
    for case in test_cases:
        result = transform_book_data({"description": case["input"]})
        assert result["description"] == case["expected"]

def test_transform_book_data_genres_handling():
    """Test genres handling logic"""
    test_cases = [
        {
            "input": ["Fiction", "Drama"],
            "expected": ["Fiction", "Drama"]
        },
        {
            "input": "Fiction,Drama",
            "expected": ["Fiction", "Drama"]
        },
        {
            "input": None,
            "expected": []
        },
        {
            "input": ["", None, "Fiction", "", "Drama"],
            "expected": ["Fiction", "Drama"]
        }
    ]
    
    for case in test_cases:
        result = transform_book_data({"genres": case["input"]})
        assert result["genres"] == case["expected"]

def test_transform_book_data_rating_handling():
    """Test rating handling logic"""
    test_cases = [
        {
            "input": 4.5,
            "expected": "4.50"
        },
        {
            "input": "4.5",
            "expected": "4.50"
        },
        {
            "input": None,
            "expected": ""
        },
        {
            "input": "invalid",
            "expected": ""
        },
        {
            "input": 0,
            "expected": ""
        }
    ]
    
    for case in test_cases:
        result = transform_book_data({"rating": case["input"]})
        assert result["rating"] == case["expected"] 