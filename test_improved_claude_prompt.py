#!/usr/bin/env python3
"""
Test script for improved Claude API emotion mapping.
This script tests the improved Claude API prompt for mapping emotions to primary emotions.
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

def test_improved_claude_prompt(emotion: str):
    """
    Test the improved Claude API prompt for mapping emotions.
    
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
        
        logger.info(f"Testing improved Claude API prompt for emotion: '{emotion}'")
        logger.info(f"Primary emotions: {primary_emotions_str}")
        
        # Call the Claude API with the improved prompt
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            system="""You are an expert in emotional analysis. Your task is to map an input emotion to the closest matching emotion from a predefined list.
IMPORTANT: Respond with ONLY the single word for the closest matching emotion FROM THE PROVIDED LIST, with no additional text, punctuation, or explanation.

Examples:
Input: 'happiness' with list "joy, sadness, fear"
Correct response: joy
Incorrect response: happiness
Incorrect response: happiness maps to joy
Incorrect response: The closest emotion is joy

Input: 'terrified' with list "joy, sadness, fear"
Correct response: fear
Incorrect response: terrified
Incorrect response: terrified maps to fear""",
            messages=[
                {
                    "role": "user", 
                    "content": f"Map the emotion '{emotion}' to the closest matching emotion FROM this list: {primary_emotions_str}. You MUST choose one of these emotions, even if '{emotion}' itself appears in the list. Respond with ONLY the emotion name from the list, nothing else."
                }
            ]
        )
        
        # Get the response text
        closest_match = response.content[0].text.strip().lower()
        
        logger.info(f"Claude API response: '{closest_match}'")
        
        # Additional processing to handle cases where the model still includes explanatory text
        if " " in closest_match:
            logger.warning(f"Response contains spaces, attempting to extract emotion...")
            
            # If there are spaces, try to extract just the emotion
            words = closest_match.split()
            # Check if any word matches a primary emotion
            for word in words:
                clean_word = word.strip(".,;:()\"'").lower()
                if clean_word in analyzer.primary_emotions:
                    closest_match = clean_word
                    logger.info(f"Extracted emotion '{closest_match}' from response")
                    break
                    
            # If no match found in words, check if response contains "maps to" pattern
            if "maps to" in closest_match:
                parts = closest_match.split("maps to")
                if len(parts) > 1:
                    potential_match = parts[1].strip(".,;:()\"'").lower()
                    if potential_match in analyzer.primary_emotions:
                        closest_match = potential_match
                        logger.info(f"Extracted emotion '{closest_match}' from 'maps to' pattern")
        
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
    test_improved_claude_prompt("escapism")
    
    # Test with a few other emotions for comparison
    test_improved_claude_prompt("excitement")
    test_improved_claude_prompt("nostalgia") 