#!/usr/bin/env python3
"""
Test script for Claude API emotion mapping.
This script tests the Claude API's ability to map emotions to primary emotions.
"""

import os
import sys
import logging
from anthropic import Anthropic
from decouple import config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the EmotionalAnalyzer to get the primary emotions list
from moodreads.analysis.claude import EmotionalAnalyzer

def test_claude_emotion_mapping(emotion: str):
    """
    Test the Claude API's ability to map an emotion to primary emotions.
    
    Args:
        emotion: The emotion to map
    """
    try:
        # Initialize the analyzer to get the primary emotions list
        analyzer = EmotionalAnalyzer()
        
        # Get the Claude API key
        api_key = config('CLAUDE_API_KEY')
        
        # Initialize the Claude client
        client = Anthropic(api_key=api_key)
        
        # Get the list of primary emotions
        primary_emotions_str = ", ".join(analyzer.primary_emotions)
        
        logger.info(f"Testing Claude API mapping for emotion: '{emotion}'")
        logger.info(f"Primary emotions: {primary_emotions_str}")
        
        # Call the Claude API
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            system=f"You are an expert in emotional analysis. Your task is to map an input emotion to the closest matching emotion from a predefined list. Respond with ONLY the closest matching emotion, no explanation.",
            messages=[
                {
                    "role": "user", 
                    "content": f"Map the emotion '{emotion}' to the closest matching emotion from this list: {primary_emotions_str}. Respond with ONLY the emotion name, nothing else."
                }
            ]
        )
        
        # Get the response text
        closest_match = response.content[0].text.strip().lower()
        
        logger.info(f"Claude API response: '{closest_match}'")
        
        # Check if the response is in the primary emotions list
        if closest_match in analyzer.primary_emotions:
            logger.info(f"✅ Valid mapping: '{emotion}' -> '{closest_match}'")
        else:
            logger.warning(f"❌ Invalid mapping: '{closest_match}' is not in the primary emotions list")
            
            # Check for partial matches
            partial_matches = [e for e in analyzer.primary_emotions if closest_match in e or e in closest_match]
            if partial_matches:
                logger.info(f"Possible partial matches: {partial_matches}")
        
        # Print the full response for debugging
        logger.debug(f"Full response: {response}")
        
    except Exception as e:
        logger.error(f"Error testing Claude API: {str(e)}")

if __name__ == "__main__":
    # Test with the "escapism" emotion
    test_claude_emotion_mapping("escapism")
    
    # Test with a few other emotions for comparison
    test_claude_emotion_mapping("excitement")
    test_claude_emotion_mapping("nostalgia") 