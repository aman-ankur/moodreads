#!/usr/bin/env python3
"""
Test script for enhanced emotional analysis using Google Books volume IDs.

This script demonstrates how to retrieve book data directly using Google Books volume IDs,
and then perform enhanced emotional analysis on the retrieved data.
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
from moodreads.analysis.claude import EmotionalAnalyzer

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

def test_emotional_analysis(volume_id):
    """Test emotional analysis using a Google Books volume ID."""
    print(f"Testing emotional analysis for volume ID: {volume_id}")
    
    # Step 1: Get book data from Google Books
    google_client = GoogleBooksAPIClient()
    book_data = google_client.get_book_by_volume_id(volume_id, use_cache=False)
    
    if not book_data:
        print("Failed to fetch book data from Google Books")
        return None
    
    print(f"\nSuccessfully fetched book: {book_data.get('title', 'Unknown')} by {book_data.get('author', 'Unknown')}")
    
    # Step 2: Integrate data (Google Books only in this case)
    integrator = BookDataIntegrator()
    integrated_data = integrator.integrate_by_google_books_id(volume_id)
    
    if not integrated_data:
        print("Failed to integrate book data")
        return None
    
    print(f"\nSuccessfully integrated book data")
    
    # Step 3: Perform emotional analysis
    analyzer = EmotionalAnalyzer()
    
    # Extract necessary data for analysis
    description = integrated_data.get('description', '')
    reviews = integrated_data.get('reviews', [])
    genres = integrated_data.get('genres', [])
    
    print(f"\nPerforming emotional analysis...")
    analysis_result = analyzer.analyze_book_enhanced(
        description,
        reviews,
        genres,
        use_cache=False,  # Force fresh analysis for testing
        book_id=f"google_{volume_id}"
    )
    
    if not analysis_result:
        print("Failed to analyze book")
        return None
    
    print(f"\nSuccessfully analyzed book")
    
    # Step 4: Display and save results
    
    # Print top emotions
    print("\nTop Emotions:")
    for emotion in analysis_result.get('emotional_profile', [])[:5]:
        print(f"- {emotion.get('emotion', 'Unknown')}: {emotion.get('intensity', 0)}/10")
    
    # Print emotional arc
    print("\nEmotional Arc:")
    arc = analysis_result.get('emotional_arc', {})
    print(f"- Beginning: {', '.join(arc.get('beginning', []))}")
    print(f"- Middle: {', '.join(arc.get('middle', []))}")
    print(f"- End: {', '.join(arc.get('end', []))}")
    
    # Print emotional keywords
    print("\nEmotional Keywords:")
    print(f"- {', '.join(analysis_result.get('emotional_keywords', []))}")
    
    # Print lasting impact
    print("\nLasting Impact:")
    print(f"- {analysis_result.get('lasting_impact', 'None')}")
    
    # Print overall emotional profile
    print("\nOverall Emotional Profile:")
    print(f"- {analysis_result.get('overall_emotional_profile', 'None')}")
    
    # Save results to JSON
    filename = f"emotional_analysis_{volume_id}.json"
    save_to_json(analysis_result, filename)
    
    return analysis_result

def main():
    parser = argparse.ArgumentParser(description="Test enhanced emotional analysis using Google Books volume IDs")
    parser.add_argument("--volume-id", help="Google Books volume ID to test")
    parser.add_argument("--url", help="Google Books URL to extract volume ID from")
    
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
    
    # Test emotional analysis
    analysis_result = test_emotional_analysis(volume_id)

if __name__ == "__main__":
    main() 