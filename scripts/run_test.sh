#!/bin/bash

# Script to run the test_advanced_scraper.py with the virtual environment

# Find the virtual environment
if [ -d ".moodreads-env" ]; then
    VENV_PATH=".moodreads-env"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
elif [ -d ".venv" ]; then
    VENV_PATH=".venv"
else
    echo "Error: Virtual environment not found"
    exit 1
fi

echo "Using virtual environment: $VENV_PATH"

# Activate the virtual environment and run the test script
source "$VENV_PATH/bin/activate"

# Run the test script with skip-analysis flag
python scripts/test_advanced_scraper.py --category science-fiction --num-books 1 --db-name moodreads_advanced_test --skip-analysis

# Check the result
if [ $? -eq 0 ]; then
    echo "Test completed successfully"
    
    # Check the database
    python scripts/check_advanced_db.py --db-name moodreads_advanced_test
else
    echo "Test failed"
fi

# Deactivate the virtual environment
deactivate 