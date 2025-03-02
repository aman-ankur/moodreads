#!/usr/bin/env python3
"""
Unit tests for the EmotionalAnalyzer class.

This module contains tests to verify the functionality of the EmotionalAnalyzer class,
ensuring that it correctly analyzes book data and handles different formats of emotional profiles.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
from typing import Dict, List, Any, Optional
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodreads.analysis.claude import EmotionalAnalyzer

class TestEmotionalAnalyzer(unittest.TestCase):
    """Test cases for the EmotionalAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the Anthropic client
        self.anthropic_patcher = patch('moodreads.analysis.claude.anthropic.Anthropic')
        self.mock_anthropic = self.anthropic_patcher.start()
        self.mock_client = self.mock_anthropic.return_value
        self.mock_client.messages.create.return_value = MagicMock()
        
        # Create a mock for the config function
        self.config_patcher = patch('moodreads.analysis.claude.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.return_value = "mock_api_key"
        
        # Create the EmotionalAnalyzer instance
        self.analyzer = EmotionalAnalyzer(cache_dir="test_cache")
        
        # Sample book data
        self.sample_book = {
            "title": "Test Book",
            "author": "Test Author",
            "description": "This is a test book description.",
            "reviews_data": [
                {"text": "This book was amazing!", "rating": 5},
                {"text": "I didn't like this book.", "rating": 2}
            ],
            "genres": ["Fiction", "Science Fiction"]
        }
        
        # Sample emotional profile
        self.sample_emotional_profile = {
            "primary_emotions": [
                {"emotion": "joy", "intensity": 8, "explanation": "The book has many joyful moments."},
                {"emotion": "sadness", "intensity": 5, "explanation": "There are some sad scenes."}
            ],
            "emotional_arc": {
                "beginning": ["curiosity", "anticipation"],
                "middle": ["tension", "fear"],
                "end": ["relief", "satisfaction"]
            },
            "emotional_keywords": ["thrilling", "heartwarming", "suspenseful"],
            "overall_tone": "A rollercoaster of emotions with a satisfying conclusion."
        }
        
        # Sample list-format emotional profile
        self.sample_list_emotional_profile = [
            {"emotion": "joy", "intensity": 8, "explanation": "The book has many joyful moments."},
            {"emotion": "sadness", "intensity": 5, "explanation": "There are some sad scenes."}
        ]
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.anthropic_patcher.stop()
        self.config_patcher.stop()
    
    def test_init(self):
        """Test initialization of EmotionalAnalyzer."""
        # Check if the client was initialized correctly
        self.mock_anthropic.assert_called_once_with(api_key="mock_api_key")
        
        # Check if the primary emotions list is not empty
        self.assertGreater(len(self.analyzer.primary_emotions), 0)
    
    @patch('moodreads.analysis.claude.Path.exists')
    @patch('moodreads.analysis.claude.open', new_callable=mock_open)
    @patch('moodreads.analysis.claude.json.load')
    def test_analyze_book_enhanced_with_cache(self, mock_json_load, mock_file, mock_exists):
        """Test analyzing a book with cache."""
        # Set up mock return value
        mock_exists.return_value = True
        mock_json_load.return_value = {
            "emotional_profile": self.sample_emotional_profile["primary_emotions"],
            "emotional_arc": self.sample_emotional_profile["emotional_arc"],
            "emotional_keywords": self.sample_emotional_profile["emotional_keywords"],
            "overall_emotional_profile": self.sample_emotional_profile["overall_tone"],
            "emotional_intensity": 6.5,
            "embedding": [0.8, 0.5, 0.0, 0.0, 0.0]
        }
        
        # Call the method
        result = self.analyzer.analyze_book_enhanced(
            description=self.sample_book["description"],
            reviews=self.sample_book["reviews_data"],
            genres=self.sample_book["genres"],
            book_id="test_book_id"
        )
        
        # Check if the cache was used
        mock_exists.assert_called_once()
        mock_file.assert_called_once()
        mock_json_load.assert_called_once()
        
        # Check if the client was not called
        self.mock_client.messages.create.assert_not_called()
        
        # Check the result
        self.assertEqual(result["emotional_profile"], self.sample_emotional_profile["primary_emotions"])
        self.assertEqual(result["emotional_arc"], self.sample_emotional_profile["emotional_arc"])
    
    @patch('moodreads.analysis.claude.Path.exists')
    @patch('moodreads.analysis.claude.json.dump')
    @patch('moodreads.analysis.claude.open', new_callable=mock_open)
    def test_analyze_book_enhanced_without_cache(self, mock_file, mock_json_dump, mock_exists):
        """Test analyzing a book without cache."""
        # Set up mock return values
        mock_exists.return_value = False
        
        # Set up mock for _analyze_description
        with patch.object(self.analyzer, '_analyze_description', return_value=self.sample_emotional_profile) as mock_analyze_description:
            # Set up mock for _analyze_reviews
            with patch.object(self.analyzer, '_analyze_reviews', return_value={"reader_emotions": []}) as mock_analyze_reviews:
                # Set up mock for _analyze_genres
                with patch.object(self.analyzer, '_analyze_genres', return_value={"genre_emotions": []}) as mock_analyze_genres:
                    # Set up mock for _create_emotional_profile
                    with patch.object(self.analyzer, '_create_emotional_profile', return_value=self.sample_emotional_profile) as mock_create_profile:
                        # Set up mock for _generate_emotion_vector
                        with patch.object(self.analyzer, '_generate_emotion_vector', return_value=np.array([0.8, 0.5, 0.0, 0.0, 0.0])) as mock_generate_vector:
                            # Call the method
                            result = self.analyzer.analyze_book_enhanced(
                                description=self.sample_book["description"],
                                reviews=self.sample_book["reviews_data"],
                                genres=self.sample_book["genres"],
                                book_id="test_book_id"
                            )
        
        # Check if the methods were called
        mock_analyze_description.assert_called_once_with(self.sample_book["description"])
        mock_analyze_reviews.assert_called_once()
        mock_analyze_genres.assert_called_once_with(self.sample_book["genres"])
        mock_create_profile.assert_called_once()
        mock_generate_vector.assert_called_once()
        
        # Check if the result was cached
        mock_file.assert_called_once()
        mock_json_dump.assert_called_once()
        
        # Check the result
        self.assertEqual(result["emotional_profile"], self.sample_emotional_profile["primary_emotions"])
        self.assertEqual(result["emotional_arc"], self.sample_emotional_profile["emotional_arc"])
    
    def test_extract_json(self):
        """Test extracting JSON from text."""
        # Test with JSON between triple backticks
        text = "Here is the JSON:\n```json\n{\"key\": \"value\"}\n```"
        json_str = self.analyzer._extract_json(text)
        self.assertEqual(json_str, "{\"key\": \"value\"}")
        
        # Test with JSON between curly braces
        text = "Here is the JSON: {\"key\": \"value\"}"
        json_str = self.analyzer._extract_json(text)
        self.assertEqual(json_str, "{\"key\": \"value\"}")
        
        # Test with no JSON
        text = "Here is no JSON."
        json_str = self.analyzer._extract_json(text)
        self.assertEqual(json_str, "{}")
    
    def test_find_closest_emotion(self):
        """Test finding the closest emotion."""
        # Test with exact match
        emotion = "joy"
        closest = self.analyzer._find_closest_emotion(emotion)
        self.assertEqual(closest, "joy")
        
        # Test with substring match
        emotion = "joyful"
        closest = self.analyzer._find_closest_emotion(emotion)
        self.assertEqual(closest, "joy")
        
        # Test with no match
        emotion = "xyz"
        closest = self.analyzer._find_closest_emotion(emotion)
        self.assertEqual(closest, self.analyzer.primary_emotions[0])
    
    def test_generate_emotion_vector_dict_format(self):
        """Test generating an emotion vector from a dictionary format emotional profile."""
        # Set up test data
        emotional_profile = self.sample_emotional_profile
        
        # Call the method
        vector = self.analyzer._generate_emotion_vector(emotional_profile)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.analyzer.primary_emotions))
        
        # Check if the emotions were mapped correctly
        joy_index = self.analyzer.primary_emotions.index("joy")
        sadness_index = self.analyzer.primary_emotions.index("sadness")
        self.assertAlmostEqual(vector[joy_index], 0.8)  # 8/10
        self.assertAlmostEqual(vector[sadness_index], 0.5)  # 5/10
    
    def test_generate_emotion_vector_list_format(self):
        """Test generating an emotion vector from a list format emotional profile."""
        # Set up test data
        emotional_profile = self.sample_list_emotional_profile
        
        # Call the method
        vector = self.analyzer._generate_emotion_vector(emotional_profile)
        
        # Check the result
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(len(vector), len(self.analyzer.primary_emotions))
        
        # Check if the emotions were mapped correctly
        joy_index = self.analyzer.primary_emotions.index("joy")
        sadness_index = self.analyzer.primary_emotions.index("sadness")
        self.assertAlmostEqual(vector[joy_index], 0.8)  # 8/10
        self.assertAlmostEqual(vector[sadness_index], 0.5)  # 5/10
    
    def test_analyze_genres(self):
        """Test analyzing genres."""
        # Set up mock response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="""
        Here's the analysis:
        ```json
        {
            "genre_emotions": [
                {"emotion": "wonder", "association_strength": 8, "genre": "Science Fiction"},
                {"emotion": "curiosity", "association_strength": 7, "genre": "Science Fiction"}
            ],
            "genre_emotional_expectations": "Science fiction often evokes a sense of wonder and curiosity."
        }
        ```
        """)]
        self.mock_client.messages.create.return_value = mock_message
        
        # Call the method
        result = self.analyzer._analyze_genres(["Science Fiction", "Adventure"])
        
        # Check if the client was called correctly
        self.mock_client.messages.create.assert_called_once()
        
        # Check the result
        self.assertEqual(len(result["genre_emotions"]), 2)
        self.assertEqual(result["genre_emotions"][0]["emotion"], "wonder")
        self.assertEqual(result["genre_emotions"][0]["association_strength"], 8)
    
    def test_analyze_genres_with_empty_genres(self):
        """Test analyzing genres with empty genres list."""
        # Call the method
        result = self.analyzer._analyze_genres([])
        
        # Check if the client was not called
        self.mock_client.messages.create.assert_not_called()
        
        # Check the result
        self.assertEqual(result["genre_emotions"], [])
        self.assertEqual(result["genre_emotional_expectations"], "")
    
    def test_analyze_genres_with_json_error(self):
        """Test analyzing genres with JSON parsing error."""
        # Set up mock response with invalid JSON
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="""
        Here's the analysis:
        ```json
        {
            "genre_emotions": [
                {"emotion": "wonder", "association_strength": 8, "genre": "Science Fiction"},
                {"emotion": "curiosity", "association_strength": 7, "genre": "Science Fiction"
            ],
            "genre_emotional_expectations": "Science fiction often evokes a sense of wonder and curiosity."
        }
        ```
        """)]
        self.mock_client.messages.create.return_value = mock_message
        
        # Call the method
        result = self.analyzer._analyze_genres(["Science Fiction", "Adventure"])
        
        # Check if the client was called correctly
        self.mock_client.messages.create.assert_called_once()
        
        # Check the result (should return default values due to JSON error)
        self.assertEqual(result["genre_emotions"], [])
        self.assertEqual(result["genre_emotional_expectations"], "")

if __name__ == "__main__":
    unittest.main() 