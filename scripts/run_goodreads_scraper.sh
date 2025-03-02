#!/bin/bash

# Script to run the Goodreads review scraper with common options

# Ensure Playwright is installed
if ! python -c "import playwright" &> /dev/null; then
    echo "Installing Playwright..."
    pip install playwright
    python -m playwright install
fi

# Default values
URL="https://www.goodreads.com/book/show/1885.Pride_and_Prejudice"
MIN_WORDS=100
MAX_REVIEWS=10
OUTPUT="goodreads_reviews.json"
FORMAT="json"
HEADLESS=true
SCROLL_DELAY=2
SCROLL_COUNT=3

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            URL="$2"
            shift 2
            ;;
        --min-words)
            MIN_WORDS="$2"
            shift 2
            ;;
        --max-reviews)
            MAX_REVIEWS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --no-headless)
            HEADLESS=false
            shift
            ;;
        --scroll-delay)
            SCROLL_DELAY="$2"
            shift 2
            ;;
        --scroll-count)
            SCROLL_COUNT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build the command
CMD="python scripts/extract_goodreads_reviews.py"
CMD+=" --url \"$URL\""
CMD+=" --min-words $MIN_WORDS"
CMD+=" --max-reviews $MAX_REVIEWS"
CMD+=" --output \"$OUTPUT\""
CMD+=" --format $FORMAT"
CMD+=" --scroll-delay $SCROLL_DELAY"
CMD+=" --scroll-count $SCROLL_COUNT"

if [ "$HEADLESS" = false ]; then
    CMD+=" --no-headless"
fi

# Print the command
echo "Running: $CMD"

# Execute the command
eval $CMD

# Check if the output file exists
if [ -f "$OUTPUT" ]; then
    echo "Success! Reviews saved to $OUTPUT"
    
    # Print a summary if JSON format
    if [ "$FORMAT" = "json" ]; then
        echo "Summary:"
        python -c "import json; data = json.load(open('$OUTPUT')); print(f\"Total reviews: {data['metadata']['review_count']}\")"
    fi
else
    echo "Error: Output file not created"
fi 