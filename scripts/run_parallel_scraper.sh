#!/bin/bash
# Run the parallel book scraper with optimal settings

# Create logs directory if it doesn't exist
mkdir -p logs

# Set environment variables if needed
# export CLAUDE_API_KEY=your_api_key_here
# export GOOGLE_BOOKS_API_KEY=your_api_key_here

# Run the script with parallel processing
echo "Starting parallel book scraper..."
python scripts/update_production_books.py \
  --categories fiction science-fiction fantasy mystery romance \
  --books-per-category 10 \
  --db-name moodreads_production \
  --timeout 300 \
  --max-category-workers 3 \
  --max-book-workers 5

echo "Parallel book scraper completed." 