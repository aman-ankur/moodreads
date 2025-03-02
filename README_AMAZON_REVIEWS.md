# Amazon Reviews Extraction and Emotional Analysis

This module provides tools for extracting book reviews from Amazon and analyzing their emotional content to enhance the MoodReads recommendation engine.

## Overview

The Amazon review extraction system is designed to complement the existing Goodreads extraction by:

1. Finding Amazon product links from Goodreads book pages
2. Fetching and parsing Amazon review pages
3. Extracting high-quality, detailed reviews
4. Analyzing the emotional content of these reviews
5. Creating comprehensive emotional profiles for books

This approach addresses the challenges faced with Goodreads review extraction and provides richer emotional data for the recommendation engine.

## Components

The system consists of three main components:

### 1. `extract_amazon_reviews.py`

This script handles the extraction of reviews from Amazon:

- Extracts Amazon product URLs from Goodreads HTML
- Fetches Amazon review pages with proper rate limiting and user agent rotation
- Parses HTML to extract review content and metadata
- Filters reviews based on quality criteria (word count, helpfulness)
- Saves raw review data to JSON files

```bash
python extract_amazon_reviews.py --goodreads-html goodreads_page.html --output amazon_reviews.json
```

### 2. `amazon_emotional_analysis.py`

This script analyzes the emotional content of Amazon reviews:

- Processes individual reviews to extract emotional signals
- Creates collective emotional profiles from multiple reviews
- Uses Claude API for deep emotional analysis
- Extracts primary emotions, emotional intensity, arcs, and keywords
- Saves enhanced review data with emotional analysis

```bash
python amazon_emotional_analysis.py --goodreads-html goodreads_page.html --book-title "Book Title" --genre "Fiction"
```

### 3. `amazon_book_scraper.py`

This script integrates the extraction and analysis into a batch processing system:

- Processes multiple books in sequence
- Handles error recovery and logging
- Implements proper rate limiting between requests
- Saves results for each book
- Provides a summary of the processing results

```bash
python amazon_book_scraper.py --input books_data.json --output-dir amazon_reviews
```

## Emotional Analysis

The emotional analysis system extracts the following information:

- **Primary emotions**: Joy, sadness, tension, comfort, fear, etc.
- **Emotional intensity**: Scale of 1-10
- **Emotional arc**: Progression of emotions throughout the book
- **Unexpected emotions**: Surprising emotional responses
- **Lasting impact**: Long-term emotional effects
- **Emotional keywords**: Key phrases and words related to emotions

This data is structured in a consistent JSON format that can be easily integrated with the recommendation engine.

## Usage

### Basic Usage

To extract and analyze reviews for a single book:

```bash
python amazon_emotional_analysis.py --goodreads-html path/to/goodreads.html --book-title "Book Title" --genre "Fiction"
```

### Batch Processing

To process multiple books:

1. Create a JSON file with book information:

```json
[
  {
    "book_id": "1234",
    "title": "Book Title 1",
    "genre": "Fiction",
    "goodreads_html_file": "path/to/goodreads1.html"
  },
  {
    "book_id": "5678",
    "title": "Book Title 2",
    "genre": "Mystery",
    "goodreads_html_file": "path/to/goodreads2.html"
  }
]
```

2. Run the batch processor:

```bash
python amazon_book_scraper.py --input books_data.json --output-dir amazon_reviews --max-reviews 10 --min-words 50
```

### Command Line Options

#### `extract_amazon_reviews.py`

- `--goodreads-html`: Path to the Goodreads HTML file
- `--amazon-url`: Direct Amazon product URL (alternative to goodreads-html)
- `--output`: Output JSON file
- `--min-words`: Minimum number of words for a review (default: 50)
- `--max-reviews`: Maximum number of reviews to extract (default: 10)
- `--book-id`: Book ID for metadata (optional)

#### `amazon_emotional_analysis.py`

- `--goodreads-html`: Path to the Goodreads HTML file
- `--amazon-url`: Direct Amazon product URL (alternative to goodreads-html)
- `--book-title`: Title of the book (for better emotional analysis)
- `--genre`: Genre of the book (for better emotional analysis)
- `--book-id`: Book ID for metadata (optional)
- `--min-words`: Minimum number of words for a review (default: 50)
- `--max-reviews`: Maximum number of reviews to extract (default: 10)
- `--output`: Output JSON file
- `--skip-individual`: Skip individual review analysis
- `--skip-collective`: Skip collective review analysis

#### `amazon_book_scraper.py`

- `--input`: Input JSON file with books data
- `--output-dir`: Directory to save output files (default: amazon_reviews)
- `--results`: Output JSON file for processing results (default: amazon_processing_results.json)
- `--min-words`: Minimum number of words for a review (default: 50)
- `--max-reviews`: Maximum number of reviews to extract (default: 10)
- `--skip-emotions`: Skip emotional analysis
- `--skip-individual`: Skip individual review analysis
- `--skip-collective`: Skip collective review analysis
- `--delay`: Delay between processing books in seconds (default: 5)

## Output Format

### Raw Reviews JSON

```json
{
  "metadata": {
    "extraction_date": "2024-03-01T12:34:56.789Z",
    "review_count": 10,
    "source": "amazon",
    "book_id": "1234",
    "book_title": "Book Title",
    "genre": "Fiction"
  },
  "reviews": [
    {
      "reviewer": "John Doe",
      "rating": 4.5,
      "title": "Great read!",
      "text": "This book was amazing...",
      "date": "March 1, 2024",
      "helpful_votes": 42,
      "word_count": 150
    },
    // More reviews...
  ]
}
```

### Enhanced Reviews with Emotional Analysis

```json
{
  "metadata": {
    "analysis_date": "2024-03-01T12:34:56.789Z",
    "book_title": "Book Title",
    "genre": "Fiction",
    "review_count": 10
  },
  "reviews": [
    {
      "reviewer": "John Doe",
      "rating": 4.5,
      "title": "Great read!",
      "text": "This book was amazing...",
      "date": "March 1, 2024",
      "helpful_votes": 42,
      "word_count": 150,
      "emotional_analysis": {
        "primary_emotions": ["joy", "wonder", "satisfaction"],
        "emotional_intensity": 8,
        "emotional_arc": "Started with curiosity, built to excitement, ended with satisfaction",
        "unexpected_emotions": ["nostalgia"],
        "lasting_impact": "Feeling of inspiration and motivation",
        "emotional_keywords": ["thrilling", "captivating", "inspiring"]
      }
    },
    // More reviews...
  ],
  "emotional_analysis": {
    "collective": {
      "primary_emotions": {
        "joy": 80,
        "wonder": 60,
        "satisfaction": 70
      },
      "emotional_intensity": 7.5,
      "emotional_arc": {
        "beginning": ["curiosity", "intrigue"],
        "middle": ["tension", "excitement"],
        "end": ["satisfaction", "fulfillment"]
      },
      "unexpected_emotions": ["nostalgia", "melancholy"],
      "lasting_impact": ["inspiration", "reflection"],
      "emotional_keywords": ["thrilling", "captivating", "inspiring", "thought-provoking"],
      "summary": "A primarily joyful and wonder-filled reading experience with moderate emotional intensity that leaves readers feeling inspired and reflective."
    }
  }
}
```

## Requirements

- Python 3.8+
- beautifulsoup4
- requests
- anthropic (Claude API)
- tqdm
- python-dotenv
- textblob (optional, for basic sentiment analysis)

## Notes

- Amazon may block requests if too many are made in a short period. The system implements rate limiting and user agent rotation to minimize this risk.
- The Claude API requires an API key, which should be set in the `.env` file as `ANTHROPIC_API_KEY`.
- The emotional analysis is computationally intensive and may take some time for large batches of books.
- For best results, provide both the book title and genre when analyzing emotions. 