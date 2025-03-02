# MoodReads Advanced Scraper

This document describes the advanced book scraper for the MoodReads project, which creates a new MongoDB database with enhanced emotional vector embeddings and additional book metadata from Google Books API.

## Overview

The advanced scraper builds upon the original MoodReads scraper with the following enhancements:

1. Uses a separate MongoDB database (`moodreads_advanced`) to store the data
2. Integrates with Google Books API to fetch additional book metadata
3. Ensures book thumbnails are stored in the database
4. Generates and stores advanced emotional vector embeddings
5. Provides more detailed logging and error handling

## Prerequisites

Before running the advanced scraper, make sure you have:

1. MongoDB installed and running
2. Python 3.8+ with required dependencies installed
3. Google Books API key (optional but recommended)
4. Claude API key for emotional analysis

## Environment Variables

The following environment variables should be set:

- `MONGODB_URI`: MongoDB connection URI (default: `mongodb://localhost:27017`)
- `GOOGLE_BOOKS_API_KEY` or `GOOGLE_API_KEY`: Google Books API key
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `CLAUDE_MODEL`: Claude model to use (default: `claude-3-opus-20240229`)

You can set these in a `.env` file in the project root.

## Usage

### Running the Advanced Scraper

To run the advanced scraper with default settings:

```bash
python scripts/scrape_books.py
```

This will scrape books from the default categories and store them in the `moodreads_advanced` database.

### Command-line Options

The scraper supports the following command-line options:

- `--categories`: List of Goodreads categories to scrape (default: fiction, mystery, science-fiction, romance, fantasy, thriller, historical-fiction, non-fiction, young-adult, horror)
- `--depth`: Number of pages to scrape per category (default: 2)
- `--batch-size`: Number of books to process in each batch (default: 5)
- `--rate-limit`: Minimum seconds between requests (default: 3.0)
- `--db-name`: MongoDB database name to use (default: moodreads_advanced)

Example with custom options:

```bash
python scripts/scrape_books.py --categories fantasy science-fiction --depth 3 --batch-size 10 --rate-limit 2.0 --db-name moodreads_custom
```

### Testing the Scraper

To test the scraper with a small number of books:

```bash
python scripts/test_advanced_scraper.py --category science-fiction --num-books 3 --db-name moodreads_advanced_test
```

### Checking the Database

To check the contents of the database:

```bash
python scripts/check_advanced_db.py --db-name moodreads_advanced
```

## Data Structure

Each book document in the database includes:

- Basic book information (title, author, ISBN, etc.)
- Google Books metadata (if available)
- Cover image URL
- Enhanced emotional profile
- Emotional vector embedding
- Reviews data
- Scraping metadata

## Emotional Vector Embeddings

The advanced scraper generates emotional vector embeddings based on:

1. Primary emotions identified in the book
2. Emotional keywords
3. Emotional intensity
4. Emotional arc

These embeddings enable more accurate mood-based book recommendations.

## Troubleshooting

If you encounter issues:

1. Check the log files in the `logs` directory
2. Verify that MongoDB is running and accessible
3. Ensure API keys are correctly set in environment variables
4. Check network connectivity for API requests

## License

This project is licensed under the MIT License - see the LICENSE file for details. 