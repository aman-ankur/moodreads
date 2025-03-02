# MoodReads Integration System

This system integrates Goodreads book data with Google Books emotional analysis to create a comprehensive book database for mood-based recommendations.

## Features

- **Goodreads Data Scraping**: Extracts book details, reviews, and cover images from Goodreads
- **Google Books API Integration**: Fetches additional book metadata and performs emotional analysis
- **MongoDB Storage**: Stores the combined data for efficient querying
- **Emotional Analysis**: Creates detailed emotional profiles for each book
- **Mood-Based Recommendations**: Recommends books based on emotional queries

## Requirements

- Python 3.7+
- MongoDB
- Claude API key (for emotional analysis)
- Google Books API key

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file:
   ```
   CLAUDE_API_KEY=your_claude_api_key
   GOOGLE_API_KEY=your_google_api_key
   MONGODB_URI=your_mongodb_connection_string
   ```

## Usage

### Process a Single Book

```bash
python integrate_emotional_analysis.py --query "To Kill a Mockingbird" --output "mockingbird_data.json"
```

### Process Multiple Books from a File

```bash
python integrate_emotional_analysis.py --file "sample_books.txt" --output "processed_books.json"
```

### Get Mood-Based Recommendations

```bash
python integrate_emotional_analysis.py --mood "inspiring and uplifting" --output "inspiring_books.json"
```

## Data Flow

1. **Book Search**: Search for a book on Goodreads
2. **Data Extraction**: Extract detailed book information and reviews
3. **Google Books Integration**: Find the same book on Google Books
4. **Emotional Analysis**: Create an emotional profile using the Claude API
5. **Data Storage**: Store the combined data in MongoDB
6. **Recommendation Engine**: Query the database for mood-based recommendations

## Emotional Profile Structure

Each book's emotional profile includes:

- **Primary Emotions**: Top emotions with intensity scores
- **Emotional Arc**: Emotional progression through the book
- **Overall Profile**: General emotional characterization
- **Unexpected Emotions**: Surprising emotional elements
- **Emotional Keywords**: Key terms related to the book's emotional content

## MongoDB Schema

Books are stored with the following structure:

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "cover_url": "URL to cover image",
  "isbn": "ISBN number",
  "description": "Book description",
  "genres": ["Genre1", "Genre2"],
  "avg_rating": 4.5,
  "ratings_count": 1000,
  "published_date": "January 1st 2000",
  "page_count": 300,
  "goodreads_url": "URL to Goodreads page",
  "google_books_id": "Google Books ID",
  "google_books_link": "URL to Google Books page",
  "reviews": [
    {
      "reviewer": "Reviewer Name",
      "rating": 5,
      "text": "Review text",
      "date": "Review date",
      "likes": 10
    }
  ],
  "emotional_profile": {
    "primary_emotions": [
      {"emotion": "Wonder", "intensity": 9.0},
      {"emotion": "Sadness", "intensity": 8.0}
    ],
    "emotional_arc": {
      "beginning": ["Curiosity", "Excitement"],
      "middle": ["Tension", "Fear"],
      "end": ["Relief", "Satisfaction"]
    },
    "overall_emotional_profile": "Bittersweet",
    "unexpected_emotions": ["Hope", "Nostalgia"],
    "emotional_keywords": ["journey", "transformation", "loss"]
  },
  "created_at": "2023-06-01T12:00:00.000Z",
  "last_updated": "2023-06-01T12:00:00.000Z"
}
```

## Performance Considerations

- The script uses caching for API calls to reduce redundant requests
- Rate limiting is implemented for Goodreads scraping to avoid IP blocks
- MongoDB indexes are created for efficient querying

## Future Improvements

- Add more advanced emotional analysis techniques
- Implement user feedback for recommendation refinement
- Expand to additional book data sources
- Add sentiment analysis for reviews
- Create a web interface for browsing recommendations 