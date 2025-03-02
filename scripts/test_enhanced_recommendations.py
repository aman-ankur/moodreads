#!/usr/bin/env python3
"""
Script to test the enhanced recommendation system.
This script allows users to enter mood queries and see recommendations
using both the standard and enhanced recommendation systems for comparison.
"""

import argparse
import logging
import sys
import json
from tabulate import tabulate
from colorama import init, Fore, Style

from moodreads.recommender.engine import RecommendationEngine

# Initialize colorama for colored output
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recommendations.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def format_book_recommendation(book, score, explanation=None, enhanced=False):
    """Format a book recommendation for display."""
    title = book.get('title', 'Unknown Title')
    author = book.get('author', 'Unknown Author')
    genres = ', '.join(book.get('genres', []))
    rating = book.get('rating', 0)
    
    # Format the output
    output = []
    
    # Add title with color based on whether it's enhanced
    color = Fore.GREEN if enhanced else Fore.BLUE
    output.append(f"{color}{title}{Style.RESET_ALL} by {author}")
    output.append(f"Rating: {rating:.1f}/5.0 | Match Score: {score:.2f}")
    output.append(f"Genres: {genres}")
    
    if explanation:
        output.append(f"Why this matches: {explanation}")
    
    # Add enhanced features if available and enhanced mode is on
    if enhanced and 'enhanced_emotional_profile' in book:
        enhanced_profile = book.get('enhanced_emotional_profile', {})
        
        # Add lasting impact if available
        lasting_impact = enhanced_profile.get('lasting_impact', '')
        if lasting_impact:
            output.append(f"Lasting Impact: {lasting_impact}")
        
        # Add unexpected emotions if available
        unexpected_emotions = enhanced_profile.get('unexpected_emotions', [])
        if unexpected_emotions:
            output.append(f"Unexpected Emotions: {', '.join(unexpected_emotions)}")
    
    return output

def get_recommendations(query, limit=5, compare=False, output_file=None):
    """
    Get book recommendations based on emotional query.
    
    Args:
        query: User's mood-based query
        limit: Maximum number of recommendations to return
        compare: Whether to compare standard and enhanced recommendations
        output_file: Optional file to save recommendations to
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # Initialize recommendation engine
        engine = RecommendationEngine()
        
        if compare:
            # Get both standard and enhanced recommendations
            standard_recommendations = engine.get_recommendations(
                query, limit=limit, include_explanation=True, use_enhanced=False
            )
            
            enhanced_recommendations = engine.get_recommendations(
                query, limit=limit, include_explanation=True, use_enhanced=True
            )
            
            # Display standard recommendations
            print("\n=== Standard Recommendations ===\n")
            if not standard_recommendations:
                print("No standard recommendations found.")
            else:
                for i, rec in enumerate(standard_recommendations, 1):
                    book = rec['book']
                    score = rec['score']
                    explanation = rec.get('explanation', '')
                    
                    print(f"\n{i}. " + "\n   ".join(format_book_recommendation(book, score, explanation)))
            
            # Display enhanced recommendations
            print("\n=== Enhanced Recommendations ===\n")
            if not enhanced_recommendations:
                print("No enhanced recommendations found.")
            else:
                for i, rec in enumerate(enhanced_recommendations, 1):
                    book = rec['book']
                    score = rec['score']
                    explanation = rec.get('explanation', '')
                    
                    print(f"\n{i}. " + "\n   ".join(format_book_recommendation(book, score, explanation, enhanced=True)))
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump({
                        'query': query,
                        'standard_recommendations': [
                            {
                                'title': rec['book'].get('title', ''),
                                'author': rec['book'].get('author', ''),
                                'score': rec['score'],
                                'explanation': rec.get('explanation', '')
                            } for rec in standard_recommendations
                        ],
                        'enhanced_recommendations': [
                            {
                                'title': rec['book'].get('title', ''),
                                'author': rec['book'].get('author', ''),
                                'score': rec['score'],
                                'explanation': rec.get('explanation', '')
                            } for rec in enhanced_recommendations
                        ]
                    }, f, indent=2)
                print(f"\nRecommendations saved to {output_file}")
        
        else:
            # Get only enhanced recommendations
            recommendations = engine.get_recommendations(
                query, limit=limit, include_explanation=True, use_enhanced=True
            )
            
            # Display recommendations
            print("\n=== Book Recommendations ===\n")
            if not recommendations:
                print("No recommendations found.")
            else:
                for i, rec in enumerate(recommendations, 1):
                    book = rec['book']
                    score = rec['score']
                    explanation = rec.get('explanation', '')
                    
                    print(f"\n{i}. " + "\n   ".join(format_book_recommendation(book, score, explanation, enhanced=True)))
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump({
                        'query': query,
                        'recommendations': [
                            {
                                'title': rec['book'].get('title', ''),
                                'author': rec['book'].get('author', ''),
                                'score': rec['score'],
                                'explanation': rec.get('explanation', '')
                            } for rec in recommendations
                        ]
                    }, f, indent=2)
                print(f"\nRecommendations saved to {output_file}")
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Get book recommendations based on emotional query"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Emotional query for book recommendations"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of recommendations to return"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare standard and enhanced recommendations"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file for recommendations (optional)"
    )
    
    args = parser.parse_args()
    
    try:
        get_recommendations(args.query, args.limit, args.compare, args.output)
    except KeyboardInterrupt:
        print("\nRecommendation process interrupted by user")
    except Exception as e:
        logger.error(f"Recommendation process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 