# Enhanced Emotional Analysis and Recommendation System

This document provides an overview of the enhanced emotional analysis and recommendation system for the Moodreads project.

## Overview

The enhanced system integrates data from multiple sources (Goodreads and Google Books) and performs comprehensive emotional analysis using the Anthropic Claude API to create rich emotional profiles for books. These profiles are then used to provide personalized book recommendations based on users' emotional needs and preferences.

## Components

### 1. Data Integration

The `BookDataIntegrator` class combines data from Goodreads and Google Books to create a unified record for each book:

- Scrapes book data and reviews from Goodreads
- Fetches additional metadata from Google Books API
- Merges the data into a comprehensive record
- Creates a combined text for emotional analysis

### 2. Enhanced Emotional Analysis

The `EmotionalAnalyzer` class uses the Anthropic Claude API to perform comprehensive emotional analysis:

- Analyzes book descriptions for primary emotional content
- Analyzes reviews for reader emotional responses
- Considers genre information as supplementary signals
- Creates a comprehensive emotional profile
- Generates an emotional vector embedding for similarity matching

The emotional profile includes:
- Primary emotions with intensity scores
- Emotional arc (beginning, middle, end)
- Emotional keywords and themes
- Unexpected emotions
- Lasting emotional impact
- Overall emotional intensity

### 3. Vector Embedding System

- **VectorEmbeddingStore**: Dedicated class for creating, managing, and retrieving vector embeddings
- **Emotion Vector Creation**: Maps emotions to positions in a fixed-dimension vector space
- **Vector Normalization**: Normalizes vectors to unit length for fair comparisons
- **Composite Vectors**: Creates weighted combinations of multiple emotional vectors
- **Efficient Similarity Search**: Implements cosine similarity for finding emotionally similar books

### 4. Enhanced Recommendation Engine

The `EnhancedRecommender` class provides personalized book recommendations based on:

- User mood queries analyzed for emotional needs
- Emotional profile matching
- Emotional keyword matching
- Emotional journey/arc matching
- Emotional intensity preferences
- Vector similarity for "books like this" recommendations

## Scripts

### Data Collection and Analysis

- `test_enhanced_data.py`: Tests the enhanced data collection and emotional analysis system
- `update_emotional_profiles.py`: Updates existing books in the database with enhanced emotional profiles

### Recommendation Testing

- `test_recommendations.py`: Tests the enhanced recommendation engine with various mood queries

## Usage Examples

### Updating Emotional Profiles

```bash
# Update all books without enhanced analysis
python scripts/update_emotional_profiles.py

# Update a limited number of books
python scripts/update_emotional_profiles.py --limit 10

# Include books that already have enhanced analysis
python scripts/update_emotional_profiles.py --include-enhanced
```

### Testing Recommendations

```bash
# Test with a specific mood query
python scripts/test_recommendations.py --query "I'm feeling sad and need something uplifting"

# Find books similar to a specific book
python scripts/test_recommendations.py --book-id <book_id>

# Test with predefined mood queries
python scripts/test_recommendations.py --predefined
```

## Emotional Analysis Process

1. **Description Analysis**: The book description is analyzed to identify primary emotions, emotional arc, and overall tone.

2. **Review Analysis**: Reader reviews are analyzed to identify emotional responses, impact, and unexpected emotions.

3. **Genre Analysis**: Genre information is used as supplementary signals for associated emotions.

4. **Profile Creation**: A comprehensive emotional profile is created by combining the analyses with appropriate weighting.

5. **Vector Generation**: An emotional vector embedding is generated for similarity matching.

## Recommendation Process

1. **Query Analysis**: The user's mood query is analyzed to identify current emotional state, desired emotional experience, and preferences.

2. **Candidate Selection**: Books with enhanced analysis and minimum ratings are selected as candidates.

3. **Similarity Calculation**: Similarity scores are calculated based on:
   - Emotional profile matching (50%)
   - Keyword matching (20%)
   - Emotional journey matching (20%)
   - Intensity matching (10%)

4. **Explanation Generation**: Personalized explanations are generated for each recommendation.

## Future Enhancements

- Implement user feedback loop to improve recommendations
- Add support for more nuanced emotional queries
- Enhance emotional journey matching with sequence alignment algorithms
- Implement collaborative filtering based on emotional preferences
- Add support for multi-language emotional analysis
- Implement advanced emotional arcs
- Incorporate user feedback to improve recommendations
- Consider user's reading history and preferences for contextual recommendations
- Optimize vector storage and retrieval mechanisms for performance
- Expand book database for broader coverage

## MoodReads Enhanced System

MoodReads is an emotional book recommendation system that matches users with books based on their emotional needs rather than traditional genre categories. This document outlines the enhanced features implemented in the system.

### Core Components

#### 1. Enhanced Data Collection

- **Multi-Source Integration**: Combines data from Goodreads and Google Books API
- **Comprehensive Book Records**: Creates unified book records with metadata from multiple sources
- **Ethical Web Scraping**: Implements rate limiting and resumable scraping functionality

#### 2. Enhanced Emotional Analysis

- **Comprehensive Analysis**: Processes book descriptions, reviews, and genre information
- **Emotional Profile Dimensions**: Captures primary emotions, emotional arcs, lasting impact, and emotional keywords
- **Claude API Integration**: Uses specialized prompts for analyzing emotional content
- Overall emotional intensity

#### 3. Vector Embedding System

- **VectorEmbeddingStore**: Dedicated class for creating, managing, and retrieving vector embeddings
- **Emotion Vector Creation**: Maps emotions to positions in a fixed-dimension vector space
- **Vector Normalization**: Normalizes vectors to unit length for fair comparisons
- **Composite Vectors**: Creates weighted combinations of multiple emotional vectors
- **Efficient Similarity Search**: Implements cosine similarity for finding emotionally similar books

#### 4. Enhanced Recommendation Engine

The `EnhancedRecommender` class provides personalized book recommendations based on:
- Emotional similarity between user mood and book profiles
- Multidimensional matching across emotional dimensions
- Personalized explanations for recommendations

### Usage

#### Processing Books for Vector Embeddings

```python
from moodreads.analysis.vector_embeddings import VectorEmbeddingStore

# Initialize the vector store
vector_store = VectorEmbeddingStore()

# Process all books with emotional profiles
total, success = vector_store.process_all_books()
print(f"Processed {total} books, {success} successful")

# Process a specific book
from moodreads.database.mongodb import MongoDBClient
db = MongoDBClient()
book = db.get_book("book_id")
success = vector_store.process_book_for_vectors(book)
```

#### Getting Recommendations by Mood

```python
from moodreads.recommendation.enhanced_recommender import EnhancedRecommender

# Initialize the recommender
recommender = EnhancedRecommender()

# Get recommendations by mood
recommendations = recommender.recommend_books(
    query="I'm feeling anxious and need something comforting",
    limit=5,
    min_rating=4.0,
    include_explanation=True
)

# Display recommendations
for i, rec in enumerate(recommendations):
    print(f"{i+1}. {rec['title']} by {rec['author']}")
    print(f"   Match Score: {rec['match_score']}%")
    print(f"   Explanation: {rec['explanation']}")
    print()
```

#### Finding Similar Books

```python
# Find books similar to a given book
similar_books = recommender.get_similar_books(book_id="book_id", limit=5)

# Display similar books
for i, book in enumerate(similar_books):
    print(f"{i+1}. {book['title']} by {book['author']}")
    print(f"   Similarity Score: {book['similarity_score']}%")
    print()
```

### Command-Line Tools

The system includes command-line tools for processing books and testing recommendations:

```bash
# Process all books with emotional profiles
python scripts/process_vectors.py --process-all

# Process a specific book
python scripts/process_vectors.py --process-book <book_id>

# Test recommendations for a mood query
python scripts/process_vectors.py --test-recommendations "feeling anxious and need comfort"

# Test finding similar books
python scripts/process_vectors.py --test-similar-books <book_id>
```

### Testing

The system includes comprehensive unit tests for all components:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python tests/test_vector_embeddings.py
```

### Future Enhancements

- Enhance emotional journey matching with sequence alignment algorithms
- Implement collaborative filtering based on emotional preferences
- Add support for multi-language emotional analysis
- Implement advanced emotional arcs
- Incorporate user feedback to improve recommendations
- Consider user's reading history and preferences for contextual recommendations
- Optimize vector storage and retrieval mechanisms for performance
- Expand book database for broader coverage 