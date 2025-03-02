"""
Pytest configuration file.
"""

import pytest
import os
from pathlib import Path

def pytest_configure(config):
    """Configure test environment."""
    # Set test environment variables
    os.environ['MONGODB_URI'] = 'mongodb://localhost:27017'
    os.environ['MONGODB_DB_NAME'] = 'moodreads_test'  # Use test database
    os.environ['CLAUDE_API_KEY'] = 'test_key'  # Mock API key
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Create test data directory if it doesn't exist
    test_data_dir = Path('tests/data')
    test_data_dir.mkdir(parents=True, exist_ok=True)

@pytest.fixture(autouse=True)
def clean_test_db():
    """Clean test database before and after each test."""
    from moodreads.database.mongodb import MongoDBClient
    
    # Get test database
    db = MongoDBClient()
    
    # Clean before test
    db.books_collection.delete_many({})
    
    yield
    
    # Clean after test
    db.books_collection.delete_many({}) 