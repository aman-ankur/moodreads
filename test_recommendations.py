from moodreads.recommender.engine import RecommendationEngine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format for readability
)

# Initialize engine
engine = RecommendationEngine()

# Test emotional profile
emotional_profile = {
    'joy': 0.7,
    'sadness': 0.1,
    'tension': 0.5,
    'comfort': 0.3,
    'inspiration': 0.8,
    'melancholy': 0.1,
    'hope': 0.9
}

# Get recommendations
recommendations = engine.get_recommendations(
    emotional_profile,
    "I want an exciting adventure story",
    5
)

print("\nTop Recommendations:")
print("=" * 80)
for book, score in recommendations:
    print(f"\nTitle: {book['title']}")
    print(f"Author: {book['author']}")
    print(f"Genres: {', '.join(book['genres'])}")
    print(f"Score: {score:.3f}")
    print(f"Description: {book['description'][:200]}...")
    print("-" * 80) 