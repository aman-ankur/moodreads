#!/usr/bin/env python
import argparse
import logging
from pathlib import Path
from typing import List, Dict
import json
from tabulate import tabulate

from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.recommender.engine import RecommendationEngine
from moodreads.database.mongodb import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_book_recommendation(book: Dict, score: float) -> List[str]:
    """Format a book recommendation for display."""
    return [
        book.get('title', 'Unknown Title'),
        book.get('author', 'Unknown Author'),
        book.get('url', 'No URL'),
        f"{score:.2%} match"
    ]

def get_recommendations(query: str, limit: int = 5) -> None:
    """Get book recommendations based on emotional query."""
    try:
        # Initialize components
        analyzer = EmotionalAnalyzer(use_cache=True)
        engine = RecommendationEngine()
        
        # Analyze the emotional query
        logger.info("Analyzing your emotional query...")
        emotional_profile, _ = analyzer.analyze(query)
        
        # Get recommendations
        logger.info("Finding matching books...")
        recommendations = engine.get_recommendations(emotional_profile, query, limit=limit)
        
        if not recommendations:
            print("\nNo matching books found.")
            return
        
        # Display recommendations
        print("\n=== Book Recommendations ===\n")
        headers = ['Title', 'Author', 'URL', 'Match Score']
        table = [
            format_book_recommendation(book, score)
            for book, score in recommendations
        ]
        print(tabulate(table, headers=headers, tablefmt='fancy_grid'))
        
        # Show emotional profile of query
        print("\nYour Query's Emotional Profile:")
        emotion_table = [[emotion, f"{score:.2%}"] for emotion, score in emotional_profile.items()]
        print(tabulate(emotion_table, ['Emotion', 'Score'], tablefmt='simple'))
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Get book recommendations based on emotional query"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Your emotional query (e.g., 'I want an uplifting and inspiring book')"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of recommendations to return"
    )
    
    args = parser.parse_args()
    
    try:
        get_recommendations(args.query, args.limit)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 