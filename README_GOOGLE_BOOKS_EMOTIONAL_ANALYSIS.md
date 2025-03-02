# Google Books Emotional Analysis

This module implements the enhanced emotional analysis system for MoodReads as specified in the technical requirements. It uses the Google Books API to fetch book data and the Claude API to perform emotional analysis on book descriptions and reviews.

## Features

- Fetch book data from Google Books API (descriptions, metadata, categories)
- Extract review snippets from Google Books
- Analyze emotional content of book descriptions using Claude API
- Analyze emotional content of reviews using Claude API
- Extract emotional signals from book genres
- Combine all emotional signals to create comprehensive emotional profiles
- Cache analysis results to improve performance and reduce API costs

## Emotional Profile Components

The emotional analysis creates a comprehensive profile with the following components:

1. **Primary Emotions**: List of emotions with intensity scores (0-10)
2. **Emotional Arc**: Emotional progression through beginning, middle, and end
3. **Unexpected Emotions**: Emotions that might be unexpected based on the genre
4. **Lasting Impact**: Description of the lasting emotional impact
5. **Emotional Keywords**: Emotional words and phrases extracted from the text
6. **Overall Emotional Profile**: Brief summary of the overall emotional profile

## Usage

### Prerequisites

1. Google Books API key (set in `.env` file as `GOOGLE_API_KEY`)
2. Claude API key (set in `.env` file as `CLAUDE_API_KEY`)

### Command Line Usage

```bash
# Search for a book by title/author
python google_books_emotional_analysis.py --query "The Great Gatsby"

# Search for a book by ISBN
python google_books_emotional_analysis.py --isbn "9780743273565"

# Search for a book by Google Books ID
python google_books_emotional_analysis.py --id "iXn5U2IzVH0C"

# Specify output file
python google_books_emotional_analysis.py --query "1984" --output "1984_analysis.json"

# Disable caching
python google_books_emotional_analysis.py --query "Pride and Prejudice" --no-cache
```

### Programmatic Usage

```python
from google_books_emotional_analysis import GoogleBooksClient, EmotionalAnalyzer

# Initialize clients
google_books = GoogleBooksClient()
analyzer = EmotionalAnalyzer()

# Get book data
book = google_books.search_book("To Kill a Mockingbird")[0]

# Get reviews
book['reviews'] = google_books.get_book_reviews(book['id'])

# Create emotional profile
emotional_profile = analyzer.create_emotional_profile(book)

# Print top emotions
for emotion in emotional_profile['primary_emotions'][:3]:
    print(f"{emotion['emotion']}: {emotion['intensity']}/10")
```

## Limitations

1. Google Books API doesn't provide full access to user reviews, only snippets
2. The emotional analysis is based on available descriptions and limited review data
3. For more comprehensive review analysis, consider integrating with other sources like Goodreads

## Integration with MoodReads

This module can be integrated with the existing MoodReads system by:

1. Using it to enhance book data during the scraping/ingestion process
2. Storing the emotional profiles in the MongoDB database
3. Using the emotional profiles for improved mood-based recommendations

## Future Enhancements

1. Integrate with additional review sources (Goodreads, Amazon, etc.)
2. Implement more sophisticated emotional arc analysis
3. Add support for analyzing book excerpts
4. Improve genre-emotion mapping with machine learning 