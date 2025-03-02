#!/usr/bin/env python3
"""
Test script for the enhanced Google Books API integration using volume IDs.

This script demonstrates how to retrieve comprehensive book data directly using
Google Books volume IDs, with a focus on obtaining high-quality book descriptions
for sentiment analysis.
"""

import sys
import json
import argparse
from pprint import pprint
import re
from pathlib import Path

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from moodreads.scraper.google_books import GoogleBooksAPIClient
from moodreads.scraper.integrator import BookDataIntegrator

def extract_volume_id_from_url(url):
    """Extract the volume ID from a Google Books URL."""
    # Common patterns for Google Books URLs
    patterns = [
        r'books\.google\.com/books\?id=([^&]+)',
        r'books\.google\.com/books/about/[^/]+/([^?]+)',
        r'google\.com/books/edition/[^/]+/([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

def test_volume_id_fetch(volume_id):
    """Test fetching book data using a volume ID."""
    print(f"Testing volume ID fetch for: {volume_id}")
    
    client = GoogleBooksAPIClient()
    book_data = client.get_book_by_volume_id(volume_id, use_cache=False)
    
    if not book_data:
        print("Failed to fetch book data")
        return None
    
    print(f"\nSuccessfully fetched book: {book_data.get('title', 'Unknown')}")
    
    # Print key information
    print("\nKey Information:")
    for key in ['title', 'author', 'publisher', 'published_date', 'page_count']:
        if key in book_data:
            print(f"{key.capitalize()}: {book_data[key]}")
    
    # Print description
    if 'google_description' in book_data:
        print("\nDescription:")
        description = book_data['google_description']
        # Print first 300 characters with ellipsis if longer
        if len(description) > 300:
            print(f"{description[:300]}...")
        else:
            print(description)
    
    # Save to JSON
    filename = f"google_books_volume_{volume_id}.json"
    save_to_json(book_data, filename)
    
    return book_data

def test_integration_by_volume_id(volume_id):
    """Test integrating book data using a volume ID."""
    print(f"Testing integration by volume ID for: {volume_id}")
    
    integrator = BookDataIntegrator()
    integrated_data = integrator.integrate_by_google_books_id(volume_id)
    
    if not integrated_data:
        print("Failed to integrate book data")
        return None
    
    print(f"\nSuccessfully integrated book: {integrated_data.get('title', 'Unknown')}")
    
    # Print key information
    print("\nKey Information:")
    for key in ['title', 'author', 'publisher', 'published_date', 'page_count']:
        if key in integrated_data:
            print(f"{key.capitalize()}: {integrated_data[key]}")
    
    # Print description
    if 'description' in integrated_data:
        print("\nDescription:")
        description = integrated_data['description']
        # Print first 300 characters with ellipsis if longer
        if len(description) > 300:
            print(f"{description[:300]}...")
        else:
            print(description)
    
    # Print data sources
    print("\nData Sources:", ", ".join(integrated_data.get('data_sources', [])))
    
    # Print analysis text length
    if 'analysis_text' in integrated_data:
        print(f"\nAnalysis Text Length: {len(integrated_data['analysis_text'])} characters")
    
    # Save to JSON
    filename = f"integrated_volume_{volume_id}.json"
    save_to_json(integrated_data, filename)
    
    return integrated_data

def main():
    parser = argparse.ArgumentParser(description="Test the enhanced Google Books API integration using volume IDs")
    parser.add_argument("--volume-id", help="Google Books volume ID to test")
    parser.add_argument("--url", help="Google Books URL to extract volume ID from")
    parser.add_argument("--integration", action="store_true", help="Test full integration with volume ID")
    
    args = parser.parse_args()
    
    # Get volume ID
    volume_id = None
    if args.volume_id:
        volume_id = args.volume_id
    elif args.url:
        volume_id = extract_volume_id_from_url(args.url)
        if volume_id:
            print(f"Extracted volume ID from URL: {volume_id}")
        else:
            print("Could not extract volume ID from URL")
            return
    else:
        # Default example: "1984" by George Orwell
        volume_id = "uyr8BAAAQBAJ"
        print(f"No volume ID or URL provided. Using default example: '1984' (volume ID: {volume_id})")
    
    # Test volume ID fetch
    book_data = test_volume_id_fetch(volume_id)
    
    # Test integration if requested
    if args.integration and book_data:
        print("\n" + "="*50)
        print("TESTING FULL INTEGRATION")
        print("="*50 + "\n")
        integrated_data = test_integration_by_volume_id(volume_id)

if __name__ == "__main__":
    main() 