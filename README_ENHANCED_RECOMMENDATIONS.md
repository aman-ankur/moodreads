# MoodReads Enhanced Recommendation System

This project implements the enhanced emotional analysis and recommendation system for MoodReads, as specified in the technical requirements. It creates comprehensive emotional profiles for books based on reviews, descriptions, and genres, enabling more accurate mood-based recommendations.

## System Overview

The enhanced recommendation system consists of three main components:

1. **Review Extraction**: Extracts reviews from Goodreads for analysis
2. **Emotional Analysis**: Analyzes reviews to create comprehensive emotional profiles
3. **Mood Recommendation**: Matches books to user mood queries based on emotional profiles

Together, these components create a powerful system that can understand the emotional content of books and match them to users' emotional preferences.

## Components

### 1. Review Extraction (`extract_goodreads_reviews.py`)

This component extracts reviews from Goodreads HTML pages:

- Parses HTML content using BeautifulSoup
- Extracts username, rating, review text, likes, and date
- Filters reviews by word count and rating
- Performs basic sentiment analysis using TextBlob
- Saves structured review data to JSON

[Learn more about Review Extraction](README_GOODREADS_EXTRACTOR.md)

### 2. Emotional Analysis (`emotional_analysis.py`)

This component performs deep emotional analysis on reviews:

- Uses Claude AI to extract nuanced emotional signals
- Identifies primary emotions and their intensity
- Maps emotional arcs throughout the book
- Captures unexpected emotional responses and lasting impact
- Extracts emotional keywords and phrases
- Creates comprehensive emotional profiles for books

[Learn more about Emotional Analysis](README_EMOTIONAL_ANALYSIS.md)

### 3. Mood Recommendation (`mood_recommendation.py`)

This component matches books to user mood queries:

- Analyzes user queries to extract emotional preferences
- Loads book emotional profiles
- Calculates multidimensional similarity scores
- Generates personalized recommendations with explanations
- Provides ranked list of books matching the user's mood

[Learn more about Mood Recommendation](README_MOOD_RECOMMENDATION.md)

### 4. Review Analysis (`analyze_reviews.py`)

This component provides statistical analysis and visualizations of reviews:

- Calculates average ratings and sentiment scores
- Generates word clouds of most frequent terms
- Creates charts of rating distributions
- Visualizes sentiment analysis results
- Saves analysis results to JSON and image files

[Learn more about Review Analysis](README_REVIEW_ANALYSIS.md)

## Workflow

The complete workflow for the enhanced recommendation system is:

1. **Extract Reviews**: 
   ```bash
   python extract_goodreads_reviews.py --html goodreads_page.html --sentiment
   ```

2. **Analyze Reviews** (optional):
   ```bash
   python analyze_reviews.py --input goodreads_reviews.json
   ```

3. **Enhance Reviews with Emotional Analysis**:
   ```bash
   python emotional_analysis.py --title "Book Title" --genre "Book Genre"
   ```

4. **Generate Recommendations**:
   ```bash
   python mood_recommendation.py --query "User mood query"
   ```

## Technical Implementation

### Emotional Analysis

The emotional analysis system implements the requirements specified in the technical document:

- **Primary emotions**: Joy, sadness, tension, comfort, etc.
- **Emotional intensity scores**: 1-10 scale for each emotion
- **Emotional arcs**: Beginning, middle, end progression
- **Lasting impact emotions**: How the book affects readers after finishing
- **Emotional keywords**: Specific phrases and terms from reviews

### Claude API Integration

The system uses Anthropic's Claude API for:

- Analyzing book reviews for emotional content
- Processing user mood queries
- Generating structured JSON output
- Providing literary analysis expertise

### Data Model

The enhanced data model includes:

- Review objects with text and metadata
- Comprehensive emotional profiles with multiple dimensions
- Emotional keywords extracted from reviews
- Emotional arc information
- Timestamps for when analysis was performed

## Requirements

- Python 3.6+
- Anthropic API key (Claude AI)
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Anthropic API key:
   - Create a `.env` file in the project directory
   - Add your API key: `ANTHROPIC_API_KEY=your_api_key_here`

4. Download required NLTK data:
   ```bash
   python -m textblob.download_corpora
   ```

## Directory Structure

```
moodreads/
├── extract_goodreads_reviews.py  # Review extraction script
├── emotional_analysis.py         # Emotional analysis script
├── mood_recommendation.py        # Recommendation script
├── analyze_reviews.py            # Review analysis script
├── requirements.txt              # Dependencies
├── README_ENHANCED_RECOMMENDATIONS.md  # Main README
├── README_GOODREADS_EXTRACTOR.md       # Review extraction docs
├── README_EMOTIONAL_ANALYSIS.md        # Emotional analysis docs
├── README_MOOD_RECOMMENDATION.md       # Recommendation docs
├── README_REVIEW_ANALYSIS.md           # Review analysis docs
├── enhanced_books/               # Directory for enhanced book profiles
└── analysis_results/             # Directory for analysis results
```

## Performance Considerations

- API calls to Claude can be expensive and time-consuming
- Consider implementing caching for emotional analysis results
- For large datasets, process books in batches
- Use appropriate MongoDB indexes for efficient emotion-based queries

## Future Enhancements

- Integration with MongoDB for storing book profiles
- Web interface for user mood queries
- Batch processing for analyzing multiple books
- Expanded genre-emotion mapping
- User feedback mechanism to improve recommendations

## License

This project is open source under the MIT License. 