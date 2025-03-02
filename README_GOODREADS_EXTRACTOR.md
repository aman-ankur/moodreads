# Goodreads Review Extractor

This Python script extracts reviews from a saved Goodreads HTML page, processes them, and saves them to a JSON file. It's designed to help you analyze book reviews without needing to use browser automation.

## Features

- Extract reviews from a saved Goodreads HTML page
- Filter reviews by minimum word count
- Filter reviews by minimum rating
- Sort reviews by likes, rating, date, or length
- Perform sentiment analysis on reviews
- Save results to a structured JSON file

## Requirements

- Python 3.6+
- BeautifulSoup4
- TextBlob (optional, for sentiment analysis)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install beautifulsoup4
pip install textblob  # Optional, for sentiment analysis
```

3. If you want to use sentiment analysis, download the required NLTK data:

```bash
python -m textblob.download_corpora
```

## Usage

### Basic Usage

```bash
python extract_goodreads_reviews.py
```

This will extract reviews from a file named `goodreads_page.html` in the current directory and save the results to `goodreads_reviews.json`.

### Advanced Usage

```bash
python extract_goodreads_reviews.py --html path/to/html/file.html --output results.json --min-words 200 --max-reviews 20 --min-rating 4 --sort likes --sentiment
```

### Command Line Arguments

- `--html`: Path to the HTML file (default: `goodreads_page.html`)
- `--output`: Output JSON file (default: `goodreads_reviews.json`)
- `--min-words`: Minimum number of words for a review to be considered (default: 100)
- `--max-reviews`: Maximum number of reviews to extract (default: 10)
- `--min-rating`: Minimum rating (1-5) to include, 0 for any rating (default: 0)
- `--sort`: Sort reviews by this field (choices: likes, rating, date, length; default: likes)
- `--sentiment`: Include sentiment analysis (requires TextBlob)

## How to Get Goodreads HTML

1. Navigate to a book's reviews page on Goodreads (e.g., https://www.goodreads.com/book/show/1885.Pride_and_Prejudice)
2. Save the complete webpage (HTML) using your browser's "Save Page As" feature
3. Use the saved HTML file as input for this script

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "metadata": {
    "extraction_date": "2025-03-01T22:29:31.787090",
    "review_count": 10
  },
  "reviews": [
    {
      "username": "User Name",
      "rating": 5,
      "text": "Review text...",
      "likes": 532,
      "date": "October 21, 2021",
      "word_count": 717,
      "sentiment": {
        "polarity": 0.19,
        "subjectivity": 0.56
      }
    },
    // More reviews...
  ]
}
```

- `polarity`: Ranges from -1.0 (negative) to 1.0 (positive)
- `subjectivity`: Ranges from 0.0 (objective) to 1.0 (subjective)

## Troubleshooting

- If no reviews are found, check if the HTML structure has changed on Goodreads
- If sentiment analysis is not working, make sure TextBlob is installed and the NLTK data is downloaded
- If the script is not extracting dates correctly, try modifying the date extraction logic in the script

## License

This project is open source and available under the MIT License. 