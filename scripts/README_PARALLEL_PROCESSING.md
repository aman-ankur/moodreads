# Parallel Processing for MoodReads Book Scraper

This document explains the parallel processing implementation for the MoodReads book scraper, which significantly improves performance by processing multiple categories and books concurrently.

## Implementation Overview

The parallel processing implementation uses a combination of:

1. **Thread-based parallelism** using `concurrent.futures.ThreadPoolExecutor` for I/O-bound operations
2. **Asynchronous processing** using `asyncio` and `aiohttp` for API calls
3. **Thread-local storage** to maintain thread-specific resources
4. **Locking mechanisms** to ensure thread safety for shared resources

## Architecture

The implementation follows a hierarchical parallel processing approach:

1. **Category-level parallelism**: Multiple book categories are processed in parallel
2. **Book-level parallelism**: Within each category, multiple books are processed concurrently
3. **API-level parallelism**: API calls (Google Books, emotional analysis) are made asynchronously

## Key Components

### 1. Parallel Category Processing

- Uses `ThreadPoolExecutor` to process multiple categories simultaneously
- Each category runs in its own thread with its own thread-local resources
- Results are collected as they complete using `as_completed`

### 2. Parallel Book Processing

- Within each category, books are processed concurrently
- Uses a separate thread pool for book-level parallelism
- Rate limiting is applied to avoid overwhelming external APIs

### 3. Asynchronous API Calls

- Google Books API calls use `aiohttp` for asynchronous HTTP requests
- Multiple API calls can be in flight simultaneously
- Semaphores limit the number of concurrent requests

### 4. Thread Safety

- Thread-local storage for scraper instances
- Locks for shared resources (database, progress tracking)
- Atomic operations for counters and shared data structures

## Usage

Run the parallel scraper using the provided script:

```bash
./scripts/run_parallel_scraper.sh
```

Or run it directly with custom parameters:

```bash
python scripts/update_production_books.py \
  --categories fiction science-fiction fantasy mystery romance \
  --books-per-category 10 \
  --db-name moodreads_production \
  --timeout 300 \
  --max-category-workers 3 \
  --max-book-workers 5
```

## Configuration Parameters

- `--categories`: Space-separated list of Goodreads categories to scrape
- `--books-per-category`: Number of books to process per category
- `--db-name`: MongoDB database name to use
- `--timeout`: Maximum time in seconds to allow for processing a single book
- `--max-category-workers`: Maximum number of categories to process in parallel
- `--max-book-workers`: Maximum number of books to process in parallel per category

## Performance Considerations

- **CPU-bound vs I/O-bound**: This implementation is optimized for I/O-bound operations (API calls, web scraping)
- **Resource usage**: Adjust worker counts based on available system resources
- **Rate limiting**: Respects rate limits for external APIs
- **Error handling**: Robust error handling ensures failures in one thread don't affect others

## Monitoring and Logging

- Detailed logging with timestamps and thread information
- Progress tracking for each category and book
- Summary statistics at completion

## Troubleshooting

If you encounter issues:

1. **Reduce concurrency**: Lower the `--max-category-workers` and `--max-book-workers` values
2. **Check API limits**: Ensure you're not exceeding rate limits for external APIs
3. **Examine logs**: Check the logs in the `logs/` directory for detailed error information
4. **Memory usage**: Monitor memory usage and reduce concurrency if memory consumption is too high 