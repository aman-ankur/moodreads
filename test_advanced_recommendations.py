#!/usr/bin/env python3
"""
Test script for advanced emotional recommendations.
This script tests the enhanced recommendation algorithm with various mood queries.
"""

import json
import logging
import argparse
from typing import Dict, List
from bson import ObjectId

from integrate_emotional_analysis import BookDataIntegrator
from google_books_emotional_analysis import EmotionalAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def calculate_emotion_similarity(target_emotions: Dict[str, float], book_emotions: Dict[str, float]) -> float:
    """Calculate similarity between two emotion dictionaries."""
    # Get all unique emotions
    all_emotions = set(list(target_emotions.keys()) + list(book_emotions.keys()))
    
    # Create vectors
    target_vector = [target_emotions.get(e, 0) for e in all_emotions]
    book_vector = [book_emotions.get(e, 0) for e in all_emotions]
    
    # Calculate cosine similarity
    dot_product = sum(a * b for a, b in zip(target_vector, book_vector))
    magnitude_target = sum(a * a for a in target_vector) ** 0.5
    magnitude_book = sum(b * b for b in book_vector) ** 0.5
    
    if magnitude_target == 0 or magnitude_book == 0:
        return 0
    
    return dot_product / (magnitude_target * magnitude_book)

def get_advanced_mood_recommendations(integrator: BookDataIntegrator, mood_query: str, limit: int = 5) -> List[Dict]:
    """
    Get advanced book recommendations based on mood with vector similarity.
    
    Args:
        integrator: BookDataIntegrator instance
        mood_query: Mood or emotional state query
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommended books with detailed emotional profiles
    """
    logger.info(f"Getting advanced recommendations for mood: {mood_query}")
    
    try:
        # Analyze the mood query to extract emotional signals
        mood_analysis = integrator.emotional_analyzer.analyze_description(
            f"A book that makes me feel {mood_query}"
        )
        
        # Extract primary emotions and their intensities from the mood analysis
        target_emotions = {e['emotion'].lower(): e['intensity'] 
                          for e in mood_analysis.get('primary_emotions', [])}
        
        print(f"\nTarget emotions for '{mood_query}':")
        for emotion, intensity in target_emotions.items():
            print(f"- {emotion}: {intensity}/10")
        
        # Find books with matching emotional profiles
        matching_books = []
        
        # Get all books from the database
        all_books = list(integrator.books_collection.find({}))
        
        for book in all_books:
            if 'emotional_profile' not in book:
                continue
            
            # Extract book emotions and intensities
            book_emotions = {e['emotion'].lower(): e['intensity'] 
                            for e in book['emotional_profile'].get('primary_emotions', [])}
            
            # Calculate vector similarity
            similarity_score = calculate_emotion_similarity(target_emotions, book_emotions)
            
            if similarity_score > 0:
                # Get matching emotions for explanation
                matching_emotions = [e for e in book['emotional_profile'].get('primary_emotions', [])
                                    if e['emotion'].lower() in target_emotions]
                
                matching_books.append({
                    'book': book,
                    'similarity_score': similarity_score,
                    'matching_emotions': matching_emotions
                })
        
        # Sort by similarity score (descending)
        matching_books.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Return top matches with enhanced data
        recommendations = []
        for match in matching_books[:limit]:
            book = match['book']
            recommendations.append({
                'title': book['title'],
                'author': book['author'],
                'cover_url': book.get('cover_url', ''),
                'match_score': int(match['similarity_score'] * 100),  # Convert to 0-100 scale
                'matching_emotions': match['matching_emotions'],
                'emotional_arc': book['emotional_profile'].get('emotional_arc', {}),
                'overall_profile': book['emotional_profile'].get('overall_emotional_profile', ''),
                'goodreads_url': book.get('goodreads_url')
            })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting advanced mood recommendations: {e}")
        return []

def test_advanced_recommendations(mood_query: str, output_file: str, limit: int = 5):
    """Test advanced mood-based recommendations."""
    logger.info(f"Testing advanced mood recommendations for: {mood_query}")
    
    integrator = BookDataIntegrator()
    recommendations = get_advanced_mood_recommendations(integrator, mood_query, limit)
    
    if recommendations:
        logger.info(f"Found {len(recommendations)} recommendations for mood: {mood_query}")
        
        # Save to file with custom encoder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
        
        logger.info(f"Saved recommendations to: {output_file}")
        
        # Display recommendations
        print(f"\n=== Advanced Book Recommendations for Mood: '{mood_query}' ===\n")
        for i, rec in enumerate(recommendations):
            print(f"{i+1}. {rec['title']} by {rec['author']}")
            print(f"   Match Score: {rec['match_score']}%")
            print(f"   Matching Emotions:")
            for emotion in rec['matching_emotions']:
                print(f"     - {emotion['emotion']}: {emotion['intensity']}/10")
            print()
        
        return True
    else:
        logger.warning(f"No recommendations found for mood: {mood_query}")
        return False

def compare_recommendation_methods(mood_query: str, output_file: str, limit: int = 5):
    """Compare original and advanced recommendation methods."""
    logger.info(f"Comparing recommendation methods for mood: {mood_query}")
    
    integrator = BookDataIntegrator()
    
    # Get original recommendations
    original_recommendations = integrator.get_mood_recommendations(mood_query, limit)
    
    # Get advanced recommendations
    advanced_recommendations = get_advanced_mood_recommendations(integrator, mood_query, limit)
    
    # Compare results
    comparison = {
        "mood_query": mood_query,
        "original_recommendations": original_recommendations,
        "advanced_recommendations": advanced_recommendations,
        "analysis": {
            "original_count": len(original_recommendations),
            "advanced_count": len(advanced_recommendations),
            "overlap": []
        }
    }
    
    # Find overlapping recommendations
    original_titles = [rec['title'] for rec in original_recommendations]
    advanced_titles = [rec['title'] for rec in advanced_recommendations]
    
    overlap = set(original_titles).intersection(set(advanced_titles))
    comparison["analysis"]["overlap"] = list(overlap)
    comparison["analysis"]["overlap_count"] = len(overlap)
    
    # Save comparison to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
    
    logger.info(f"Saved comparison to: {output_file}")
    
    # Display comparison summary
    print(f"\n=== Recommendation Method Comparison for Mood: '{mood_query}' ===\n")
    print(f"Original method found {len(original_recommendations)} books")
    print(f"Advanced method found {len(advanced_recommendations)} books")
    print(f"Overlap: {len(overlap)} books")
    
    print("\nOriginal Top 3:")
    for i, rec in enumerate(original_recommendations[:3]):
        print(f"{i+1}. {rec['title']} (Match Score: {rec['match_score']})")
    
    print("\nAdvanced Top 3:")
    for i, rec in enumerate(advanced_recommendations[:3]):
        print(f"{i+1}. {rec['title']} (Match Score: {rec['match_score']}%)")
    
    return comparison

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Test advanced emotional recommendations')
    parser.add_argument('--mood', help='Mood query for recommendations')
    parser.add_argument('--compare', action='store_true', help='Compare original and advanced methods')
    parser.add_argument('--output', default='advanced_recommendations.json', help='Output JSON file')
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of recommendations')
    
    args = parser.parse_args()
    
    if args.mood:
        if args.compare:
            compare_recommendation_methods(args.mood, args.output, args.limit)
        else:
            test_advanced_recommendations(args.mood, args.output, args.limit)
    else:
        # Run default tests with various mood queries
        test_moods = [
            "wonder and excitement",
            "fear and oppression",
            "outrage and sadness",
            "reflection and melancholy",
            "joy and comfort",
            "tension and curiosity"
        ]
        
        for i, mood in enumerate(test_moods):
            output_file = f"advanced_{mood.replace(' ', '_')}.json"
            print(f"\n\nTEST {i+1}: {mood}")
            print("=" * 50)
            test_advanced_recommendations(mood, output_file)

if __name__ == '__main__':
    main() 