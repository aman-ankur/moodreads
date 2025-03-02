# Enhanced Emotional Analysis for Book Reviews

This tool performs deep emotional analysis on book reviews using Claude AI, extracting nuanced emotional signals to create comprehensive emotional profiles for books. It's designed to enhance the MoodReads recommendation system by providing richer emotional data beyond basic sentiment analysis.

## Features

- **Deep Emotional Analysis**:
  - Identifies primary emotions in reviews (joy, sadness, tension, comfort, etc.)
  - Assigns emotional intensity scores
  - Maps emotional arcs/progression throughout the book
  - Identifies unexpected emotional responses
  - Captures lasting emotional impact
  - Extracts emotional keywords and phrases

- **Analysis Modes**:
  - Individual review analysis
  - Collective analysis of all reviews for a book
  - Genre-aware emotional analysis

- **Integration with MoodReads**:
  - Creates comprehensive emotional profiles for books
  - Enhances recommendation matching based on emotional dimensions
  - Supports the emotional fingerprinting of books

## Requirements

- Python 3.6+
- Anthropic API key (Claude AI)
- Dependencies listed in `requirements.txt`

## Installation

1. Ensure you have Python installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
   - Create a `.env` file in the project directory
   - Add your API key: `ANTHROPIC_API_KEY=your_api_key_here`
   - Or set it as an environment variable: `export ANTHROPIC_API_KEY=your_api_key_here`

## Usage

Basic usage:

```bash
python emotional_analysis.py --title "Pride and Prejudice" --genre "Classic Literature"
```

This will:
- Load reviews from the default file (`goodreads_reviews.json`)
- Perform collective emotional analysis on all reviews
- Save enhanced reviews to `enhanced_reviews.json`

### Command Line Arguments

- `--input`: Specify the input JSON file with reviews (default: `goodreads_reviews.json`)
- `--output`: Specify the output file for enhanced reviews (default: `enhanced_reviews.json`)
- `--title`: Book title (optional, but recommended for better analysis)
- `--genre`: Book genre (optional, but recommended for better analysis)
- `--individual`: Analyze each review individually (default: False)
- `--collective`: Analyze all reviews collectively (default: True)
- `--no-collective`: Skip collective analysis

Example with individual review analysis:

```bash
python emotional_analysis.py --title "Pride and Prejudice" --genre "Classic Literature" --individual
```

## Output Format

The script enhances the original reviews JSON with emotional analysis data:

```json
{
  "metadata": {
    "extraction_date": "2023-03-01T12:34:56.789012",
    "review_count": 10,
    "emotional_analysis_date": "2023-03-02T12:34:56.789012"
  },
  "reviews": [
    {
      "username": "User123",
      "rating": 5,
      "text": "Review text...",
      "date": "January 1, 2023",
      "word_count": 150,
      "sentiment": {
        "polarity": 0.8,
        "subjectivity": 0.6
      },
      "emotional_analysis": {
        "primary_emotions": [
          {"emotion": "joy", "intensity": 8},
          {"emotion": "admiration", "intensity": 7}
        ],
        "emotional_arc": {
          "beginning": ["curiosity", "amusement"],
          "middle": ["frustration", "anticipation"],
          "end": ["satisfaction", "joy"]
        },
        "unexpected_emotions": ["melancholy"],
        "lasting_impact": "A sense of warmth and satisfaction that lingers",
        "emotional_keywords": ["delightful", "charming", "witty"],
        "overall_emotional_profile": "A predominantly joyful experience with moments of tension"
      }
    },
    // More reviews...
  ],
  "book_emotional_profile": {
    "primary_emotions": [
      {"emotion": "joy", "intensity": 8},
      {"emotion": "admiration", "intensity": 7},
      {"emotion": "amusement", "intensity": 6}
    ],
    "emotional_arc": {
      "beginning": ["curiosity", "amusement"],
      "middle": ["frustration", "anticipation", "tension"],
      "end": ["satisfaction", "joy", "contentment"]
    },
    "unexpected_emotions": ["melancholy", "indignation"],
    "lasting_impact": "Readers consistently describe a lasting sense of satisfaction and warmth",
    "emotional_keywords": ["delightful", "charming", "witty", "clever", "romantic"],
    "overall_emotional_profile": "Pride and Prejudice evokes primarily positive emotions centered around joy, amusement, and satisfaction, with a narrative arc that moves from curiosity through tension to resolution and contentment."
  }
}
```

## Integration with MoodReads Recommendation System

This emotional analysis tool addresses the requirements specified in the MoodReads enhancement plan:

1. **Extracts nuanced emotional signals** from Goodreads reviews
2. **Creates comprehensive emotional profiles** for each book with multiple dimensions
3. **Identifies emotional arcs** throughout the book
4. **Captures lasting emotional impact** described by readers
5. **Extracts emotional keywords** for better matching with user queries

The enhanced data can be used to:
- Match user mood queries with appropriate books
- Recommend books based on desired emotional journeys
- Provide explanations for why a book was recommended based on emotional matching

## Performance Considerations

- API calls to Claude can be expensive and time-consuming
- Use the `--individual` flag sparingly, as it analyzes each review separately
- Consider implementing caching for emotional analysis results
- For large datasets, process books in batches

## Troubleshooting

- **API Key Issues**: Ensure your Anthropic API key is correctly set in the `.env` file or as an environment variable
- **JSON Parsing Errors**: If Claude's response can't be parsed as JSON, the script will save the raw response
- **Rate Limiting**: The script includes delays between API calls to avoid rate limiting

## License

This project is open source under the MIT License. 