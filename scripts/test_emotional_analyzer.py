#!/usr/bin/env python3
"""
Test script to verify that the EmotionalAnalyzer class correctly handles JSON parsing errors.

This script tests the JSON parsing functionality in the EmotionalAnalyzer class.
"""

import os
import sys
import logging
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodreads.analysis.claude import EmotionalAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_extract_json():
    """Test extracting JSON from different text formats."""
    try:
        # Initialize the analyzer
        with patch('moodreads.analysis.claude.anthropic.Anthropic'):
            with patch('moodreads.analysis.claude.config'):
                analyzer = EmotionalAnalyzer(cache_dir="test_cache")
                
                # Test cases
                test_cases = [
                    # JSON between triple backticks
                    (
                        """Here is the JSON:
                        ```json
                        {"key": "value", "array": [1, 2, 3]}
                        ```
                        """,
                        '{"key": "value", "array": [1, 2, 3]}'
                    ),
                    # JSON between curly braces
                    (
                        "Here is the JSON: {\"key\": \"value\", \"array\": [1, 2, 3]}",
                        '{\"key\": \"value\", \"array\": [1, 2, 3]}'
                    ),
                    # No JSON
                    (
                        "Here is no JSON.",
                        "{}"
                    )
                ]
                
                logger.info("Testing _extract_json method")
                
                for i, (text, expected) in enumerate(test_cases):
                    logger.info(f"Test case {i+1}")
                    
                    # Extract JSON
                    json_str = analyzer._extract_json(text)
                    
                    # Verify that the JSON was extracted correctly
                    assert json_str == expected, f"JSON extraction failed: {json_str} != {expected}"
                    
                    # Verify that the extracted JSON is valid
                    try:
                        json_obj = json.loads(json_str)
                        logger.info(f"Parsed JSON: {json_obj}")
                    except json.JSONDecodeError as e:
                        assert False, f"Extracted JSON is not valid: {e}"
                
                logger.info("Test passed: _extract_json method works correctly")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_analyze_genres_with_valid_json():
    """Test analyzing genres with valid JSON response."""
    try:
        # Initialize the analyzer with mocks
        with patch('moodreads.analysis.claude.anthropic.Anthropic') as mock_anthropic:
            with patch('moodreads.analysis.claude.config'):
                # Set up mock client
                mock_client = mock_anthropic.return_value
                mock_client.messages.create.return_value = MagicMock()
                
                # Set up mock response
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text="""
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
                mock_client.messages.create.return_value = mock_response
                
                # Create analyzer
                analyzer = EmotionalAnalyzer(cache_dir="test_cache")
                analyzer.client = mock_client
                
                # Test genres
                genres = ["Science Fiction", "Adventure"]
                
                logger.info("Testing _analyze_genres with valid JSON")
                
                # Analyze genres
                result = analyzer._analyze_genres(genres)
                
                # Verify that the client was called
                mock_client.messages.create.assert_called_once()
                
                # Verify the result
                assert "genre_emotions" in result, "Missing genre_emotions in result"
                assert len(result["genre_emotions"]) == 2, f"Incorrect number of emotions: {len(result['genre_emotions'])}"
                assert result["genre_emotions"][0]["emotion"] == "wonder", f"Incorrect emotion: {result['genre_emotions'][0]['emotion']}"
                assert result["genre_emotions"][0]["association_strength"] == 8, f"Incorrect strength: {result['genre_emotions'][0]['association_strength']}"
                
                logger.info("Test passed: _analyze_genres works with valid JSON")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_analyze_genres_with_invalid_json():
    """Test analyzing genres with invalid JSON response."""
    try:
        # Initialize the analyzer with mocks
        with patch('moodreads.analysis.claude.anthropic.Anthropic') as mock_anthropic:
            with patch('moodreads.analysis.claude.config'):
                # Set up mock client
                mock_client = mock_anthropic.return_value
                mock_client.messages.create.return_value = MagicMock()
                
                # Set up mock response with invalid JSON (missing closing bracket)
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text="""
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
                mock_client.messages.create.return_value = mock_response
                
                # Create analyzer
                analyzer = EmotionalAnalyzer(cache_dir="test_cache")
                analyzer.client = mock_client
                
                # Test genres
                genres = ["Science Fiction", "Adventure"]
                
                logger.info("Testing _analyze_genres with invalid JSON")
                
                # Analyze genres
                result = analyzer._analyze_genres(genres)
                
                # Verify that the client was called
                mock_client.messages.create.assert_called_once()
                
                # Verify the result (should return default values due to JSON error)
                assert "genre_emotions" in result, "Missing genre_emotions in result"
                assert result["genre_emotions"] == [], f"Incorrect genre_emotions: {result['genre_emotions']}"
                assert result["genre_emotional_expectations"] == "", f"Incorrect expectations: {result['genre_emotional_expectations']}"
                
                logger.info("Test passed: _analyze_genres handles invalid JSON correctly")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_analyze_genres_with_missing_comma():
    """Test analyzing genres with JSON response missing a comma."""
    try:
        # Initialize the analyzer with mocks
        with patch('moodreads.analysis.claude.anthropic.Anthropic') as mock_anthropic:
            with patch('moodreads.analysis.claude.config'):
                # Set up mock client
                mock_client = mock_anthropic.return_value
                mock_client.messages.create.return_value = MagicMock()
                
                # Set up mock response with JSON missing a comma
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text="""
                Here's the analysis:
                ```json
                {
                    "genre_emotions": [
                        {"emotion": "wonder", "association_strength": 8, "genre": "Science Fiction"}
                        {"emotion": "curiosity", "association_strength": 7, "genre": "Science Fiction"}
                    ],
                    "genre_emotional_expectations": "Science fiction often evokes a sense of wonder and curiosity."
                }
                ```
                """)]
                mock_client.messages.create.return_value = mock_response
                
                # Create analyzer
                analyzer = EmotionalAnalyzer(cache_dir="test_cache")
                analyzer.client = mock_client
                
                # Test genres
                genres = ["Science Fiction", "Adventure"]
                
                logger.info("Testing _analyze_genres with JSON missing a comma")
                
                # Analyze genres
                result = analyzer._analyze_genres(genres)
                
                # Verify that the client was called
                mock_client.messages.create.assert_called_once()
                
                # Verify the result (should have fixed the missing comma)
                assert "genre_emotions" in result, "Missing genre_emotions in result"
                assert len(result["genre_emotions"]) == 2, f"Incorrect number of emotions: {len(result['genre_emotions'])}"
                assert result["genre_emotions"][0]["emotion"] == "wonder", f"Incorrect emotion: {result['genre_emotions'][0]['emotion']}"
                assert result["genre_emotions"][0]["association_strength"] == 8, f"Incorrect strength: {result['genre_emotions'][0]['association_strength']}"
                assert result["genre_emotional_expectations"] == "Science fiction often evokes a sense of wonder and curiosity.", f"Incorrect expectations: {result['genre_emotional_expectations']}"
                
                logger.info("Test passed: _analyze_genres handles JSON with missing comma correctly")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_analyze_genres_with_no_json():
    """Test analyzing genres with response containing no JSON."""
    try:
        # Initialize the analyzer with mocks
        with patch('moodreads.analysis.claude.anthropic.Anthropic') as mock_anthropic:
            with patch('moodreads.analysis.claude.config'):
                # Set up mock client
                mock_client = mock_anthropic.return_value
                mock_client.messages.create.return_value = MagicMock()
                
                # Set up mock response with no JSON
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text="""
                Here's the analysis:
                Science fiction often evokes a sense of wonder and curiosity.
                Adventure stories typically involve excitement and anticipation.
                """)]
                mock_client.messages.create.return_value = mock_response
                
                # Create analyzer
                analyzer = EmotionalAnalyzer(cache_dir="test_cache")
                analyzer.client = mock_client
                
                # Test genres
                genres = ["Science Fiction", "Adventure"]
                
                logger.info("Testing _analyze_genres with no JSON")
                
                # Analyze genres
                result = analyzer._analyze_genres(genres)
                
                # Verify that the client was called
                mock_client.messages.create.assert_called_once()
                
                # Verify the result (should return default values due to no JSON)
                assert "genre_emotions" in result, "Missing genre_emotions in result"
                assert result["genre_emotions"] == [], f"Incorrect genre_emotions: {result['genre_emotions']}"
                assert result["genre_emotional_expectations"] == "", f"Incorrect expectations: {result['genre_emotional_expectations']}"
                
                logger.info("Test passed: _analyze_genres handles response with no JSON correctly")
                return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("extract_json", test_extract_json),
        ("analyze_genres_with_valid_json", test_analyze_genres_with_valid_json),
        ("analyze_genres_with_invalid_json", test_analyze_genres_with_invalid_json),
        ("analyze_genres_with_missing_comma", test_analyze_genres_with_missing_comma),
        ("analyze_genres_with_no_json", test_analyze_genres_with_no_json)
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