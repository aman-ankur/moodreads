#!/usr/bin/env python3
"""
Test script to verify that the VectorEmbeddingStore class correctly handles different formats of emotional profiles.

This script tests the vector embedding generation with different emotional profile formats.
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodreads.analysis.vector_embeddings import VectorEmbeddingStore

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_generate_vector_from_dict_format():
    """Test generating a vector from a dictionary format emotional profile."""
    try:
        # Initialize the vector store with mocks
        with patch('moodreads.analysis.vector_embeddings.MongoDBClient') as mock_db:
            with patch('moodreads.analysis.vector_embeddings.EmotionalAnalyzer') as mock_analyzer:
                # Set up mock analyzer
                mock_analyzer_instance = mock_analyzer.return_value
                mock_analyzer_instance.primary_emotions = [
                    "joy", "sadness", "anger", "fear", "surprise", 
                    "disgust", "trust", "anticipation", "love", "hope"
                ]
                
                # Create vector store
                vector_store = VectorEmbeddingStore()
                vector_store.analyzer = mock_analyzer_instance
                
                # Dictionary format emotional profile
                dict_emotional_profile = {
                    "primary_emotions": [
                        {"emotion": "joy", "intensity": 8},
                        {"emotion": "sadness", "intensity": 5},
                        {"emotion": "anticipation", "intensity": 7}
                    ],
                    "emotional_arc": {
                        "beginning": ["curiosity", "anticipation"],
                        "middle": ["tension", "fear"],
                        "end": ["relief", "satisfaction"]
                    }
                }
                
                logger.info("Testing vector generation with dictionary format emotional profile")
                
                # Generate vector
                vector = vector_store._generate_vector_from_primary_emotions(dict_emotional_profile)
                
                # Verify that the vector is a numpy array
                assert isinstance(vector, np.ndarray), "Vector is not a numpy array"
                
                # Verify that the vector has the correct length
                assert len(vector) == len(mock_analyzer_instance.primary_emotions), "Vector has incorrect length"
                
                # Verify that the vector has non-zero elements
                assert np.any(vector > 0), "Vector has no non-zero elements"
                
                # Check specific values
                joy_index = mock_analyzer_instance.primary_emotions.index("joy")
                sadness_index = mock_analyzer_instance.primary_emotions.index("sadness")
                anticipation_index = mock_analyzer_instance.primary_emotions.index("anticipation")
                
                assert vector[joy_index] == 0.8, f"Joy value incorrect: {vector[joy_index]}"
                assert vector[sadness_index] == 0.5, f"Sadness value incorrect: {vector[sadness_index]}"
                assert vector[anticipation_index] == 0.7, f"Anticipation value incorrect: {vector[anticipation_index]}"
                
                logger.info(f"Generated vector with shape {vector.shape}")
                logger.info(f"Non-zero elements: {np.count_nonzero(vector)}")
                
                # Print non-zero elements for debugging
                for i, value in enumerate(vector):
                    if value > 0:
                        logger.info(f"Emotion: {mock_analyzer_instance.primary_emotions[i]}, Value: {value}")
                
                logger.info("Test passed: Vector generation with dictionary format works correctly")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_generate_vector_from_list_format():
    """Test generating a vector from a list format emotional profile."""
    try:
        # Initialize the vector store with mocks
        with patch('moodreads.analysis.vector_embeddings.MongoDBClient') as mock_db:
            with patch('moodreads.analysis.vector_embeddings.EmotionalAnalyzer') as mock_analyzer:
                # Set up mock analyzer
                mock_analyzer_instance = mock_analyzer.return_value
                mock_analyzer_instance.primary_emotions = [
                    "joy", "sadness", "anger", "fear", "surprise", 
                    "disgust", "trust", "anticipation", "love", "hope"
                ]
                
                # Create vector store
                vector_store = VectorEmbeddingStore()
                vector_store.analyzer = mock_analyzer_instance
                
                # List format emotional profile
                list_emotional_profile = [
                    {"emotion": "joy", "intensity": 8},
                    {"emotion": "sadness", "intensity": 5},
                    {"emotion": "anticipation", "intensity": 7}
                ]
                
                logger.info("Testing vector generation with list format emotional profile")
                
                # Generate vector
                vector = vector_store._generate_vector_from_primary_emotions(list_emotional_profile)
                
                # Verify that the vector is a numpy array
                assert isinstance(vector, np.ndarray), "Vector is not a numpy array"
                
                # Verify that the vector has the correct length
                assert len(vector) == len(mock_analyzer_instance.primary_emotions), "Vector has incorrect length"
                
                # Verify that the vector has non-zero elements
                assert np.any(vector > 0), "Vector has no non-zero elements"
                
                # Check specific values
                joy_index = mock_analyzer_instance.primary_emotions.index("joy")
                sadness_index = mock_analyzer_instance.primary_emotions.index("sadness")
                anticipation_index = mock_analyzer_instance.primary_emotions.index("anticipation")
                
                assert vector[joy_index] == 0.8, f"Joy value incorrect: {vector[joy_index]}"
                assert vector[sadness_index] == 0.5, f"Sadness value incorrect: {vector[sadness_index]}"
                assert vector[anticipation_index] == 0.7, f"Anticipation value incorrect: {vector[anticipation_index]}"
                
                logger.info(f"Generated vector with shape {vector.shape}")
                logger.info(f"Non-zero elements: {np.count_nonzero(vector)}")
                
                # Print non-zero elements for debugging
                for i, value in enumerate(vector):
                    if value > 0:
                        logger.info(f"Emotion: {mock_analyzer_instance.primary_emotions[i]}, Value: {value}")
                
                logger.info("Test passed: Vector generation with list format works correctly")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_generate_emotion_vector_with_different_formats():
    """Test the generate_emotion_vector method with different emotional profile formats."""
    try:
        # Initialize the vector store with mocks
        with patch('moodreads.analysis.vector_embeddings.MongoDBClient') as mock_db:
            with patch('moodreads.analysis.vector_embeddings.EmotionalAnalyzer') as mock_analyzer:
                # Set up mock analyzer
                mock_analyzer_instance = mock_analyzer.return_value
                mock_analyzer_instance.primary_emotions = [
                    "joy", "sadness", "anger", "fear", "surprise", 
                    "disgust", "trust", "anticipation", "love", "hope"
                ]
                
                # Create vector store
                vector_store = VectorEmbeddingStore()
                vector_store.analyzer = mock_analyzer_instance
                
                # Different formats of emotional profiles
                test_profiles = [
                    # Dictionary format
                    {
                        "primary_emotions": [
                            {"emotion": "joy", "intensity": 8},
                            {"emotion": "sadness", "intensity": 5}
                        ]
                    },
                    # List format
                    [
                        {"emotion": "joy", "intensity": 8},
                        {"emotion": "sadness", "intensity": 5}
                    ],
                    # User query format
                    {
                        "current_emotional_state": ["sad", "anxious"],
                        "desired_emotional_experience": ["happy", "inspired"],
                        "emotional_journey": "From sadness to joy",
                        "intensity_preference": "moderate",
                        "emotional_keywords": ["uplifting", "heartwarming"]
                    }
                ]
                
                logger.info("Testing generate_emotion_vector with different formats")
                
                for i, profile in enumerate(test_profiles):
                    logger.info(f"Testing format {i+1}: {type(profile)}")
                    
                    # Generate vector
                    vector = vector_store.generate_emotion_vector(profile)
                    
                    # Verify that the vector is a numpy array
                    assert isinstance(vector, np.ndarray), "Vector is not a numpy array"
                    
                    # Verify that the vector has the correct length
                    assert len(vector) == len(mock_analyzer_instance.primary_emotions), "Vector has incorrect length"
                    
                    logger.info(f"Generated vector with shape {vector.shape}")
                    logger.info(f"Non-zero elements: {np.count_nonzero(vector)}")
                
                logger.info("Test passed: generate_emotion_vector works with different formats")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_process_book_with_different_profile_formats():
    """Test processing books with different emotional profile formats."""
    try:
        # Initialize the vector store with mocks
        with patch('moodreads.analysis.vector_embeddings.MongoDBClient') as mock_db:
            with patch('moodreads.analysis.vector_embeddings.EmotionalAnalyzer') as mock_analyzer:
                # Set up mock analyzer
                mock_analyzer_instance = mock_analyzer.return_value
                mock_analyzer_instance.primary_emotions = [
                    "joy", "sadness", "anger", "fear", "surprise", 
                    "disgust", "trust", "anticipation", "love", "hope"
                ]
                
                # Set up mock database
                mock_db_instance = mock_db.return_value
                mock_db_instance.books_collection = MagicMock()
                
                # Create vector store
                vector_store = VectorEmbeddingStore()
                vector_store.analyzer = mock_analyzer_instance
                vector_store.db = mock_db_instance
                
                # Books with different emotional profile formats
                test_books = [
                    # Book with dictionary format emotional profile
                    {
                        "_id": "book1",
                        "title": "Test Book 1",
                        "author": "Test Author 1",
                        "emotional_profile": {
                            "primary_emotions": [
                                {"emotion": "joy", "intensity": 8},
                                {"emotion": "sadness", "intensity": 5}
                            ]
                        }
                    },
                    # Book with list format emotional profile
                    {
                        "_id": "book2",
                        "title": "Test Book 2",
                        "author": "Test Author 2",
                        "emotional_profile": [
                            {"emotion": "joy", "intensity": 8},
                            {"emotion": "sadness", "intensity": 5}
                        ]
                    }
                ]
                
                logger.info("Testing process_book_for_vectors with different profile formats")
                
                for i, book in enumerate(test_books):
                    logger.info(f"Testing book {i+1} with profile format: {type(book['emotional_profile'])}")
                    
                    # Process book
                    result = vector_store.process_book_for_vectors(book)
                    
                    # Verify that the book was processed successfully
                    assert result, f"Failed to process book {i+1}"
                    
                    # Verify that the book was updated in the database
                    mock_db_instance.books_collection.update_one.assert_called()
                    
                    logger.info(f"Book {i+1} processed successfully")
                
                logger.info("Test passed: process_book_for_vectors works with different profile formats")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("generate_vector_from_dict_format", test_generate_vector_from_dict_format),
        ("generate_vector_from_list_format", test_generate_vector_from_list_format),
        ("generate_emotion_vector_with_different_formats", test_generate_emotion_vector_with_different_formats),
        ("process_book_with_different_profile_formats", test_process_book_with_different_profile_formats)
    ]
    
    results = []
    
    for name, test_func in tests:
        logger.info(f"\n{'=' * 50}\nRunning test: {name}\n{'=' * 50}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test {name} failed with exception: {str(e)}")
            results.append((name, False))
    
    # Print summary
    logger.info("\n\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("=" * 50)
    logger.info(f"OVERALL: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    run_all_tests() 