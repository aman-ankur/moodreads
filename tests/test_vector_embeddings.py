#!/usr/bin/env python3
"""
Unit tests for the VectorEmbeddingStore class.

This module contains tests to verify the functionality of the VectorEmbeddingStore class,
ensuring that it correctly generates vector embeddings from different formats of emotional profiles.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import numpy as np
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodreads.analysis.vector_embeddings import VectorEmbeddingStore

class TestVectorEmbeddingStore(unittest.TestCase):
    """Test cases for the VectorEmbeddingStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the MongoDB client
        self.db_patcher = patch('moodreads.analysis.vector_embeddings.MongoDBClient')
        self.mock_db = self.db_patcher.start()
        self.mock_db_instance = self.mock_db.return_value
        self.mock_db_instance.books_collection = MagicMock()
        
        # Create a mock for the EmotionalAnalyzer
        self.analyzer_patcher = patch('moodreads.analysis.vector_embeddings.EmotionalAnalyzer')
        self.mock_analyzer = self.analyzer_patcher.start()
        self.mock_analyzer_instance = self.mock_analyzer.return_value
        
        # Set up primary emotions for the analyzer
        self.mock_analyzer_instance.primary_emotions = [
            "joy", "sadness", "anger", "fear", "surprise", 
            "disgust", "trust", "anticipation", "love", "hope"
        ]
        
        # Create the VectorEmbeddingStore instance
        self.vector_store = VectorEmbeddingStore()
        
        # Replace the real instances with mocks
        self.vector_store.db = self.mock_db_instance
        self.vector_store.analyzer = self.mock_analyzer_instance
        
        # Sample emotional profile in dictionary format
        self.dict_emotional_profile = {
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
        
        # Sample emotional profile in list format
        self.list_emotional_profile = [
            {"emotion": "joy", "intensity": 8},
            {"emotion": "sadness", "intensity": 5},
            {"emotion": "anticipation", "intensity": 7}
        ]
        
        # Sample book with emotional profile
        self.sample_book = {
            "_id": "test_book_id",
            "title": "Test Book",
            "author": "Test Author",
            "emotional_profile": self.dict_emotional_profile
        }
        
        # Sample user query analysis
        self.user_query_analysis = {
            "current_emotional_state": ["sad", "anxious"],
            "desired_emotional_experience": ["happy", "inspired"],
            "emotional_journey": "From sadness to joy",
            "intensity_preference": "moderate",
            "emotional_keywords": ["uplifting", "heartwarming"]
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.db_patcher.stop()
        self.analyzer_patcher.stop()
    
    def test_init(self):
        """Test initialization of VectorEmbeddingStore."""
        # Check if the database indexes were created
        self.mock_db_instance.books_collection.create_index.assert_called()
        
        # Check if the emotion mappings dictionary is not empty
        self.assertGreater(len(self.vector_store.emotion_mappings), 0)
    
    def test_generate_vector_from_dict_emotional_profile(self):
        """Test generating a vector from a dictionary format emotional profile."""
        # Call the method
        vector = self.vector_store._generate_vector_from_primary_emotions(self.dict_emotional_profile)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.mock_analyzer_instance.primary_emotions))
        
        # Check if the emotions were mapped correctly
        joy_index = self.mock_analyzer_instance.primary_emotions.index("joy")
        sadness_index = self.mock_analyzer_instance.primary_emotions.index("sadness")
        anticipation_index = self.mock_analyzer_instance.primary_emotions.index("anticipation")
        
        self.assertAlmostEqual(vector[joy_index], 0.8)  # 8/10
        self.assertAlmostEqual(vector[sadness_index], 0.5)  # 5/10
        self.assertAlmostEqual(vector[anticipation_index], 0.7)  # 7/10
    
    def test_generate_vector_from_list_emotional_profile(self):
        """Test generating a vector from a list format emotional profile."""
        # Call the method
        vector = self.vector_store._generate_vector_from_primary_emotions(self.list_emotional_profile)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.mock_analyzer_instance.primary_emotions))
        
        # Check if the emotions were mapped correctly
        joy_index = self.mock_analyzer_instance.primary_emotions.index("joy")
        sadness_index = self.mock_analyzer_instance.primary_emotions.index("sadness")
        anticipation_index = self.mock_analyzer_instance.primary_emotions.index("anticipation")
        
        self.assertAlmostEqual(vector[joy_index], 0.8)  # 8/10
        self.assertAlmostEqual(vector[sadness_index], 0.5)  # 5/10
        self.assertAlmostEqual(vector[anticipation_index], 0.7)  # 7/10
    
    def test_generate_emotion_vector_with_dict_profile(self):
        """Test generating an emotion vector from a dictionary emotional profile."""
        # Call the method
        vector = self.vector_store.generate_emotion_vector(self.dict_emotional_profile)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.mock_analyzer_instance.primary_emotions))
    
    def test_generate_emotion_vector_with_list_profile(self):
        """Test generating an emotion vector from a list emotional profile."""
        # Call the method
        vector = self.vector_store.generate_emotion_vector(self.list_emotional_profile)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.mock_analyzer_instance.primary_emotions))
    
    def test_generate_emotion_vector_with_user_query(self):
        """Test generating an emotion vector from a user query analysis."""
        # Call the method
        vector = self.vector_store.generate_emotion_vector(self.user_query_analysis)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.mock_analyzer_instance.primary_emotions))
    
    def test_normalize_vector(self):
        """Test normalizing a vector."""
        # Create a test vector
        vector = np.array([3.0, 4.0, 0.0, 0.0])
        
        # Call the method
        normalized = self.vector_store.normalize_vector(vector)
        
        # Check the result
        self.assertIsInstance(normalized, np.ndarray)
        self.assertEqual(len(normalized), len(vector))
        
        # Check if the vector was normalized correctly (length should be 1)
        self.assertAlmostEqual(np.linalg.norm(normalized), 1.0)
        
        # Check specific values
        self.assertAlmostEqual(normalized[0], 0.6)  # 3/5
        self.assertAlmostEqual(normalized[1], 0.8)  # 4/5
    
    def test_normalize_zero_vector(self):
        """Test normalizing a zero vector."""
        # Create a test vector
        vector = np.zeros(4)
        
        # Call the method
        normalized = self.vector_store.normalize_vector(vector)
        
        # Check the result
        self.assertIsInstance(normalized, np.ndarray)
        self.assertEqual(len(normalized), len(vector))
        
        # Check if the vector was not changed (should still be all zeros)
        self.assertTrue(np.all(normalized == 0))
    
    def test_create_composite_vector(self):
        """Test creating a composite vector."""
        # Create test vectors
        vector1 = np.array([1.0, 0.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0, 0.0])
        
        # Call the method with equal weights
        composite = self.vector_store.create_composite_vector([vector1, vector2])
        
        # Check the result
        self.assertIsInstance(composite, np.ndarray)
        self.assertEqual(len(composite), len(vector1))
        
        # Check if the vectors were combined correctly
        self.assertAlmostEqual(composite[0], 0.5)  # 0.5 * 1.0
        self.assertAlmostEqual(composite[1], 0.5)  # 0.5 * 1.0
    
    def test_create_composite_vector_with_weights(self):
        """Test creating a composite vector with custom weights."""
        # Create test vectors
        vector1 = np.array([1.0, 0.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0, 0.0])
        
        # Call the method with custom weights
        composite = self.vector_store.create_composite_vector([vector1, vector2], weights=[0.7, 0.3])
        
        # Check the result
        self.assertIsInstance(composite, np.ndarray)
        self.assertEqual(len(composite), len(vector1))
        
        # Check if the vectors were combined correctly
        self.assertAlmostEqual(composite[0], 0.7)  # 0.7 * 1.0
        self.assertAlmostEqual(composite[1], 0.3)  # 0.3 * 1.0
    
    def test_cosine_similarity(self):
        """Test calculating cosine similarity."""
        # Create test vectors
        vector1 = np.array([1.0, 0.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0, 0.0])
        vector3 = np.array([0.7, 0.7, 0.0, 0.0])
        
        # Call the method
        similarity1_2 = self.vector_store._cosine_similarity(vector1, vector2)
        similarity1_3 = self.vector_store._cosine_similarity(vector1, vector3)
        
        # Check the result
        self.assertAlmostEqual(similarity1_2, 0.0)  # Orthogonal vectors
        # The correct value is 0.7 / sqrt(0.7^2 + 0.7^2) = 0.7 / sqrt(0.98) = 0.7071...
        self.assertAlmostEqual(similarity1_3, 0.7071, places=4)  # Cosine similarity between [1,0,0,0] and [0.7,0.7,0,0]
    
    def test_cosine_similarity_with_different_dimensions(self):
        """Test calculating cosine similarity with vectors of different dimensions."""
        # Create test vectors
        vector1 = np.array([1.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0, 0.0])
        
        # Call the method
        similarity = self.vector_store._cosine_similarity(vector1, vector2)
        
        # Check the result
        self.assertAlmostEqual(similarity, 0.0)  # Orthogonal vectors
    
    def test_process_book_for_vectors(self):
        """Test processing a book to generate vector embeddings."""
        # Set up mock for generate_emotion_vector
        with patch.object(self.vector_store, 'generate_emotion_vector', return_value=np.array([0.8, 0.5, 0.0, 0.0])) as mock_generate_vector:
            # Set up mock for normalize_vector
            with patch.object(self.vector_store, 'normalize_vector', return_value=np.array([0.85, 0.53, 0.0, 0.0])) as mock_normalize_vector:
                # Call the method
                result = self.vector_store.process_book_for_vectors(self.sample_book)
        
        # Check if the methods were called correctly
        mock_generate_vector.assert_called_once_with(self.dict_emotional_profile)
        mock_normalize_vector.assert_called_once()
        
        # Check if the book was updated in the database
        self.mock_db_instance.books_collection.update_one.assert_called_once()
        args, kwargs = self.mock_db_instance.books_collection.update_one.call_args
        self.assertEqual(args[0], {'_id': 'test_book_id'})
        self.assertEqual(args[1]['$set']['embedding'], [0.85, 0.53, 0.0, 0.0])
        
        # Check the result
        self.assertTrue(result)
    
    def test_process_book_for_vectors_no_emotional_profile(self):
        """Test processing a book without an emotional profile."""
        # Create a book without an emotional profile
        book = {
            "_id": "test_book_id",
            "title": "Test Book",
            "author": "Test Author"
        }
        
        # Call the method
        result = self.vector_store.process_book_for_vectors(book)
        
        # Check if the book was not updated in the database
        self.mock_db_instance.books_collection.update_one.assert_not_called()
        
        # Check the result
        self.assertFalse(result)
    
    def test_find_closest_emotion(self):
        """Test finding the closest emotion."""
        # Test with exact match
        emotion = "joy"
        closest = self.vector_store._find_closest_emotion(emotion)
        self.assertEqual(closest, "joy")
        
        # Test with substring match
        emotion = "joyful"
        closest = self.vector_store._find_closest_emotion(emotion)
        self.assertEqual(closest, "joy")
        
        # Test with no match
        emotion = "xyz"
        closest = self.vector_store._find_closest_emotion(emotion)
        self.assertEqual(closest, self.mock_analyzer_instance.primary_emotions[0])
    
    def test_map_to_primary_emotions(self):
        """Test mapping emotions to primary emotions."""
        # Mock the emotion_mappings dictionary
        self.vector_store.emotion_mappings = {
            "bored": ["sadness", "melancholy"],
            "happy": ["joy", "excitement"]
        }
        
        # Test with direct mapping
        emotion = "bored"
        mapped = self.vector_store._map_to_primary_emotions(emotion)
        self.assertIn("sadness", mapped)
        self.assertIn("melancholy", mapped)
        
        # Test with partial match
        emotion = "boring"
        mapped = self.vector_store._map_to_primary_emotions(emotion)
        self.assertIn("sadness", mapped)
        self.assertIn("melancholy", mapped)
        
        # Test with no mapping
        with patch.object(self.vector_store, '_find_closest_emotion', return_value="joy"):
            emotion = "xyz"
            mapped = self.vector_store._map_to_primary_emotions(emotion)
            self.assertIn("joy", mapped)

if __name__ == "__main__":
    unittest.main() 