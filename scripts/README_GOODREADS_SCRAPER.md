# Goodreads Review Scraper

This script extracts top reviews from Goodreads book pages using Playwright to handle dynamic content loading.

## Prerequisites

- Python 3.7+
- Playwright

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
python -m playwright install
```

## Usage

Run the script with default settings to extract reviews from Pride and Prejudice:

```bash
python scripts/extract_goodreads_reviews.py
```

### Command Line Arguments

- `--url`: URL of the Goodreads book page (default: Pride and Prejudice)
- `--min-words`: Minimum word count for reviews (default: 100)
- `--max-reviews`: Maximum number of reviews to extract (default: 10)
- `--output`: Output file path (default: goodreads_reviews.json)
- `--format`: Output format, either "json" or "csv" (default: json)
- `--headless`: Run browser in headless mode (default: True)
- `--no-headless`: Run browser in visible mode for debugging
- `--scroll-delay`: Delay between scrolls in seconds (default: 2)
- `--scroll-count`: Number of times to scroll down (default: 3)

### Examples

Extract reviews from a different book:

```bash
python scripts/extract_goodreads_reviews.py --url "https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye"
```

Extract reviews with at least 200 words:

```bash
python scripts/extract_goodreads_reviews.py --min-words 200
```

Save reviews in CSV format:

```bash
python scripts/extract_goodreads_reviews.py --format csv --output reviews.csv
```

Run in visible mode for debugging:

```bash
python scripts/extract_goodreads_reviews.py --no-headless
```

Adjust scrolling behavior to load more reviews:

```bash
python scripts/extract_goodreads_reviews.py --scroll-count 5 --scroll-delay 3
```

## Output Format

### JSON

The JSON output includes metadata and a list of reviews:

```json
{
  "metadata": {
    "extraction_date": "2023-03-01T12:34:56.789012",
    "review_count": 5
  },
  "reviews": [
    {
      "username": "User123",
      "rating": 4.0,
      "text": "Review text...",
      "date": "January 1, 2023",
      "word_count": 150
    },
    ...
  ]
}
```

### CSV

The CSV output includes columns for username, rating, text, date, and word count.

## Troubleshooting

If you encounter issues with the script:

1. Make sure you have installed Playwright browsers with `python -m playwright install`
2. Check that the Goodreads page structure hasn't changed
3. Try increasing the timeout values in the script if pages are loading slowly
4. Run with `--no-headless` to see the browser in action and debug issues
5. Increase `--scroll-count` and `--scroll-delay` if not enough reviews are being loaded

## Notes

- The script respects Goodreads' robots.txt and includes appropriate delays between actions
- Review extraction may vary based on Goodreads' dynamic content loading
- The script filters reviews to include only those meeting the minimum word count 