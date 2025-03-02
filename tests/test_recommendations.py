import pytest
import numpy as np
from moodreads.recommender.engine import RecommendationEngine
from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.database.mongodb import MongoDBClient

@pytest.fixture
def sample_book():
    return {
        'id': '123',
        'title': 'Test Book',
        'description': 'A test book about emotions',
        'emotional_profile': {
            'joy': 0.8,
            'sadness': 0.2,
            'anger': 0.1,
            'fear': 0.3
        },
        'embedding': np.random.rand(384).tolist(),  # MiniLM embedding size
        'rating': 4.5,
        'genres': ['Fiction', 'Drama']
    }

@pytest.fixture
def mongodb_client(monkeypatch):
    class MockDB:
        def __init__(self):
            self.books = {}
            
        def get_books(self, query=None):
            return list(self.books.values())
            
        def get_book(self, book_id):
            return self.books.get(book_id)
            
        def update_book(self, book_id, update):
            if book_id in self.books:
                self.books[book_id].update(update)
            else:
                self.books[book_id] = update
    
    mock_db = MockDB()
    monkeypatch.setattr(MongoDBClient, '__init__', lambda x: None)
    monkeypatch.setattr(MongoDBClient, 'get_books', mock_db.get_books)
    monkeypatch.setattr(MongoDBClient, 'get_book', mock_db.get_book)
    monkeypatch.setattr(MongoDBClient, 'update_book', mock_db.update_book)
    return mock_db

@pytest.fixture
def recommendation_engine(monkeypatch, mongodb_client):
    # Mock the EmotionalAnalyzer to avoid API calls
    def mock_analyze(self, text):
        return {
            'joy': 0.7,
            'sadness': 0.3,
            'anger': 0.2,
            'fear': 0.4
        }, "Mocked analysis"
    
    monkeypatch.setattr(EmotionalAnalyzer, 'analyze', mock_analyze)
    engine = RecommendationEngine()
    engine.db = mongodb_client
    return engine

def test_emotional_similarity_calculation(recommendation_engine):
    query_profile = {'joy': 0.8, 'sadness': 0.2}
    book_profile = {'joy': 0.7, 'sadness': 0.3}
    
    similarity = recommendation_engine._calculate_emotional_match(query_profile, book_profile)
    assert 0 <= similarity <= 1
    assert similarity > 0.9  # Should be very similar

def test_get_recommendations(recommendation_engine, sample_book, mongodb_client):
    # Add sample book to mock DB
    mongodb_client.books['123'] = sample_book
    
    # Test recommendations
    emotional_profile = {'joy': 0.7, 'sadness': 0.3}
    recommendations = recommendation_engine.get_recommendations(
        emotional_profile=emotional_profile,
        user_text="I want a happy book",
        limit=5
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5
    if recommendations:
        assert isinstance(recommendations[0], dict)
        assert 'title' in recommendations[0]

def test_recommendation_format(recommendation_engine, sample_book, mongodb_client):
    # Add multiple sample books
    for i in range(3):
        book = sample_book.copy()
        book['id'] = f'book_{i}'
        book['title'] = f'Book {i}'
        mongodb_client.books[f'book_{i}'] = book
    
    recommendations = recommendation_engine.get_recommendations(
        emotional_profile={'joy': 0.8, 'sadness': 0.2},
        user_text="I want an uplifting book",
        limit=3
    )
    
    assert len(recommendations) <= 3
    for book in recommendations:
        assert isinstance(book, dict)
        assert 'title' in book
        assert 'emotional_profile' in book

def test_empty_database(monkeypatch):
    # Create a fresh engine with empty mock DB
    class EmptyMockDB:
        def get_books(self, query=None):
            return []
        
        def get_book(self, book_id):
            return None
            
        def update_book(self, book_id, update):
            pass
    
    empty_db = EmptyMockDB()
    engine = RecommendationEngine()
    engine.db = empty_db
    
    recommendations = engine.get_recommendations(
        emotional_profile={'joy': 0.5},
        user_text="Any book",
        limit=5
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) == 0

def test_missing_emotional_profile(recommendation_engine, mongodb_client):
    # Book without emotional profile
    book = {
        'id': 'no_profile',
        'title': 'No Profile Book',
        'description': 'A book without emotional profile',
        'embedding': np.random.rand(384).tolist()
    }
    mongodb_client.books['no_profile'] = book
    
    recommendations = recommendation_engine.get_recommendations(
        emotional_profile={'joy': 0.5},
        user_text="Any book",
        limit=5
    )
    
    # Should still work but might rank this book lower
    assert isinstance(recommendations, list)

def test_integration_with_analyzer(recommendation_engine, sample_book, mongodb_client):
    mongodb_client.books['123'] = sample_book
    
    # Test with analyzer output
    analyzer = EmotionalAnalyzer()
    emotional_profile, _ = analyzer.analyze("I want a happy and uplifting book")
    
    recommendations = recommendation_engine.get_recommendations(
        emotional_profile=emotional_profile,
        user_text="I want a happy and uplifting book",
        limit=5
    )
    
    assert isinstance(recommendations, list)
    if recommendations:
        assert isinstance(recommendations[0], dict)
        assert 'title' in recommendations[0] 