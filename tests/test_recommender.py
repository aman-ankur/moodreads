import pytest
from moodreads.recommender.engine import RecommendationEngine

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