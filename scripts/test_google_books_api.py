#!/usr/bin/env python3
"""
Test script to explore the Google Books API response for a single book.
This will help us understand what data is available through the API.
"""

import sys
import json
import requests
import argparse
from pprint import pprint
from pathlib import Path

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from decouple import config

def fetch_book_by_isbn(isbn, api_key=None):
    """Fetch book data from Google Books API using ISBN."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    
    params = {
        'q': f"isbn:{isbn}",
        'maxResults': 1,
        'printType': 'books',
        'projection': 'FULL'  # Request full projection for more details
    }
    
    if api_key:
        params['key'] = api_key
    
    print(f"Fetching data for ISBN: {isbn}")
    response = requests.get(base_url, params=params, timeout=10)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None
    
    return response.json()

def fetch_book_by_title_author(title, author, api_key=None):
    """Fetch book data from Google Books API using title and author."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    
    params = {
        'q': f"intitle:{title} inauthor:{author}",
        'maxResults': 1,
        'printType': 'books',
        'projection': 'FULL'  # Request full projection for more details
    }
    
    if api_key:
        params['key'] = api_key
    
    print(f"Fetching data for title: '{title}' by author: '{author}'")
    response = requests.get(base_url, params=params, timeout=10)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None
    
    return response.json()

def fetch_volume_by_id(volume_id, api_key=None):
    """Fetch a specific volume by its ID, which might provide more details."""
    base_url = f"https://www.googleapis.com/books/v1/volumes/{volume_id}"
    
    params = {
        'projection': 'FULL'  # Request full projection for more details
    }
    
    if api_key:
        params['key'] = api_key
    
    print(f"Fetching volume details for ID: {volume_id}")
    response = requests.get(base_url, params=params, timeout=10)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None
    
    return response.json()

def save_response(response, filename):
    """Save the API response to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(response, f, indent=2)
    print(f"Response saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Test the Google Books API with a single book")
    parser.add_argument("--isbn", help="ISBN of the book to fetch")
    parser.add_argument("--title", help="Title of the book to fetch")
    parser.add_argument("--author", help="Author of the book to fetch")
    parser.add_argument("--volume-id", help="Google Books volume ID to fetch directly")
    parser.add_argument("--save", action="store_true", help="Save the response to a file")
    
    args = parser.parse_args()
    
    # Get API key from environment
    api_key = config('GOOGLE_BOOKS_API_KEY', default=None)
    
    if not api_key:
        print("Warning: No API key found. Requests may be rate limited.")
    
    # Fetch book data
    if args.volume_id:
        response = fetch_volume_by_id(args.volume_id, api_key)
    elif args.isbn:
        response = fetch_book_by_isbn(args.isbn, api_key)
    elif args.title and args.author:
        response = fetch_book_by_title_author(args.title, args.author, api_key)
    else:
        # Default example
        print("No ISBN, title/author, or volume ID provided. Using default example: 'Jane Eyre' by 'Charlotte Bronte'")
        response = fetch_book_by_title_author("Jane Eyre", "Charlotte Bronte", api_key)
    
    if not response:
        print("No data returned from API")
        return
    
    # For search results, we need to handle the items array
    if 'items' in response:
        item = response['items'][0]
        volume_id = item['id']
        
        # Optionally fetch more detailed information using the volume ID
        print(f"\nFound volume ID: {volume_id}")
        print("Fetching detailed information for this volume...")
        detailed_response = fetch_volume_by_id(volume_id, api_key)
        
        if detailed_response:
            response = detailed_response
        else:
            print("Could not fetch detailed information, using search result instead.")
    
    # Print volume info
    print("\nBook Information:")
    if 'volumeInfo' in response:
        volume_info = response['volumeInfo']
    else:
        volume_info = response  # Direct volume response
        
    for key, value in volume_info.items():
        if isinstance(value, dict) or isinstance(value, list):
            print(f"{key}: {json.dumps(value, indent=2)}")
        else:
            print(f"{key}: {value}")
    
    # Check for additional data that might be useful
    print("\nAdditional Data:")
    for key in response:
        if key != 'volumeInfo':
            print(f"\n{key}:")
            pprint(response[key])
    
    # Save the full response if requested
    if args.save:
        if args.volume_id:
            identifier = args.volume_id
        elif args.isbn:
            identifier = args.isbn
        else:
            identifier = f"{args.title}_{args.author}".replace(" ", "_")
        
        filename = f"google_books_{identifier}.json"
        save_response(response, filename)

if __name__ == "__main__":
    main() 