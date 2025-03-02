# MoodReads Vector-Based Recommendation System

This module enhances the MoodReads application with vector-based emotional recommendations, providing more accurate and nuanced book suggestions based on user mood queries.

## Overview

The vector-based recommendation system transforms emotional profiles of books into high-dimensional vectors, enabling similarity-based matching between user mood queries and book emotional content. This approach offers several advantages over traditional text-based search:

- **Semantic Understanding**: Captures the nuanced relationships between different emotions
- **Improved Matching**: Finds books with similar emotional profiles even when exact terms don't match
- **Quantifiable Similarity**: Provides match scores based on vector similarity

## Components

The system consists of the following components:

1. **Vector Embeddings Module** (`vector_embeddings.py`): Core module for generating, storing, and querying vector embeddings.
2. **Test Vector Embeddings** (`test_vector_embeddings.py`): Script for testing the vector embeddings functionality.
3. **Test API** (`test_api.py`): FastAPI application for testing the vector-based recommendations.
4. **Test Client** (`test_client.html`): Simple HTML interface for interacting with the API.
5. **Run Tests** (`run_tests.sh`): Shell script to run the tests.

## How It Works

1. **Vector Generation**: Emotional profiles from books are converted into high-dimensional vectors where each dimension represents an emotion.
2. **Vector Normalization**: Vectors are normalized to unit length to focus on the emotional pattern rather than intensity.
3. **Similarity Calculation**: Cosine similarity is used to find books with similar emotional patterns.
4. **Mood Query Processing**: User mood queries are analyzed to extract emotional signals and converted to vectors.
5. **Recommendation Ranking**: Books are ranked by similarity score and returned with match percentages.

## Installation Requirements

- Python 3.7+
- MongoDB (with text search capabilities)
- Required Python packages:
  - pymongo
  - numpy
  - fastapi
  - uvicorn
  - pydantic
  - dotenv

## Setup

1. Ensure MongoDB is running and accessible.
2. Set up environment variables in a `.env` file:
   ```
   MONGODB_URI=mongodb://localhost:27017/moodreads
   ```
3. Install required packages:
   ```
   pip install pymongo numpy fastapi uvicorn pydantic python-dotenv
   ```

## Usage

### Running Tests

The included `run_tests.sh` script provides a simple way to test the system:

```bash
./run_tests.sh
```

This will:
1. Test the vector embeddings with a sample emotional profile
2. Get recommendations for the mood "wonder and excitement"
3. Start the API server for testing with the HTML client

### Using the API

The API provides a simple endpoint for getting recommendations:

```
POST /api/advanced-recommendations
{
  "mood": "excited and curious",
  "limit": 5
}
```

Response:
```json
[
  {
    "title": "Book Title",
    "author": "Author Name",
    "cover_url": "https://example.com/cover.jpg",
    "match_score": 85,
    "matching_emotions": [
      {"emotion": "Excitement", "intensity": 8.5},
      {"emotion": "Curiosity", "intensity": 7.2}
    ],
    "goodreads_url": "https://goodreads.com/book/show/123"
  },
  ...
]
```

### Using the Test Client

Open `test_client.html` in a web browser while the API server is running to:
- Select from preset moods or enter custom mood descriptions
- View book recommendations with match scores and emotional details
- See cover images and links to Goodreads

## Integration with MoodReads

To integrate this system with the main MoodReads application:

1. Import the `VectorEmbeddingStore` class from `vector_embeddings.py`
2. Initialize the store with your MongoDB connection
3. Use the `get_recommendations_by_mood` method to retrieve recommendations

Example:
```python
from vector_embeddings import VectorEmbeddingStore

# Initialize the vector store
vector_store = VectorEmbeddingStore()

# Get recommendations
recommendations = vector_store.get_recommendations_by_mood("excited and curious", limit=5)

# Process and display recommendations
for book in recommendations:
    print(f"{book['title']} by {book['author']} - {book['match_score']}% match")
```

## Performance Considerations

- The current implementation loads all vectors into memory for similarity calculation, which may not scale well for very large collections.
- For production use with large datasets, consider using a dedicated vector database or implementing approximate nearest neighbor search.
- MongoDB's Atlas Search can be used for vector search in production environments.

## Future Enhancements

- Implement approximate nearest neighbor search for better performance with large collections
- Add user feedback loop to improve recommendations based on user interactions
- Explore dimensionality reduction techniques to optimize vector storage and retrieval
- Integrate with a dedicated vector database for improved scalability 