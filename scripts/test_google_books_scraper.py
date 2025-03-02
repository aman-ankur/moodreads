#!/usr/bin/env python3
"""
Test script to explore scraping data from Google Books webpages.
This will help us understand what additional data is available through the web interface
that isn't provided by the API.
"""

import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup
from pprint import pprint
from pathlib import Path
import re

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_google_books_page(book_id):
    """Fetch the Google Books webpage for a specific book ID."""
    url = f"https://www.google.com/books/edition/_/{book_id}?hl=en"
    
    print(f"Fetching Google Books webpage for ID: {book_id}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None

def extract_book_data(html_content):
    """Extract book data from the Google Books webpage HTML."""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    book_data = {}
    
    # Basic book information
    try:
        book_data['title'] = soup.select_one('h1').text.strip() if soup.select_one('h1') else None
        book_data['author'] = soup.select_one('a[href*="inauthor"]').text.strip() if soup.select_one('a[href*="inauthor"]') else None
        
        # Publisher info
        publisher_text = soup.find(string=re.compile('Publisher'))
        if publisher_text and publisher_text.find_parent('tr'):
            publisher_row = publisher_text.find_parent('tr')
            book_data['publisher'] = publisher_row.select_one('td:nth-of-type(2)').text.strip() if publisher_row.select_one('td:nth-of-type(2)') else None
        
        # Publication date
        pub_date_text = soup.find(string=re.compile('Published'))
        if pub_date_text and pub_date_text.find_parent('tr'):
            pub_date_row = pub_date_text.find_parent('tr')
            book_data['published_date'] = pub_date_row.select_one('td:nth-of-type(2)').text.strip() if pub_date_row.select_one('td:nth-of-type(2)') else None
        
        # Page count
        length_text = soup.find(string=re.compile('Length'))
        if length_text and length_text.find_parent('tr'):
            length_row = length_text.find_parent('tr')
            page_count_text = length_row.select_one('td:nth-of-type(2)').text.strip() if length_row.select_one('td:nth-of-type(2)') else None
            if page_count_text:
                book_data['page_count'] = re.search(r'(\d+)', page_count_text).group(1) if re.search(r'(\d+)', page_count_text) else None
    except Exception as e:
        print(f"Error extracting basic book information: {e}")
    
    # Common terms and phrases
    try:
        common_terms_heading = soup.find(string=re.compile('Common terms and phrases'))
        if common_terms_heading and common_terms_heading.find_parent():
            common_terms_section = common_terms_heading.find_parent().find_next_sibling()
            if common_terms_section:
                terms = [term.text.strip() for term in common_terms_section.select('a')]
                book_data['common_terms'] = terms
    except Exception as e:
        print(f"Error extracting common terms: {e}")
    
    # Popular passages
    try:
        popular_passages = []
        popular_passages_heading = soup.find(string=re.compile('Popular passages'))
        if popular_passages_heading and popular_passages_heading.find_parent():
            passages_section = popular_passages_heading.find_parent().find_next_siblings()
            for section in passages_section:
                if section.name == 'h3':  # Stop when we hit the next heading
                    break
                
                passage_text = section.select_one('div.passage-text')
                if passage_text:
                    passage_info = section.select_one('div.passage-info')
                    passage_data = {
                        'text': passage_text.text.strip(),
                        'info': passage_info.text.strip() if passage_info else None
                    }
                    popular_passages.append(passage_data)
            
            book_data['popular_passages'] = popular_passages
    except Exception as e:
        print(f"Error extracting popular passages: {e}")
    
    # About the author
    try:
        about_author_heading = soup.find(string=re.compile('About the author'))
        if about_author_heading and about_author_heading.find_parent():
            about_section = about_author_heading.find_parent().find_next_sibling()
            if about_section:
                book_data['about_author'] = about_section.text.strip()
    except Exception as e:
        print(f"Error extracting author information: {e}")
    
    # Description
    try:
        description = soup.select_one('div[itemprop="description"]')
        if description:
            book_data['description'] = description.text.strip()
    except Exception as e:
        print(f"Error extracting description: {e}")
    
    return book_data

def save_data(data, filename):
    """Save the extracted data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Test scraping data from Google Books webpages")
    parser.add_argument("--book-id", required=True, help="Google Books ID (from the URL)")
    parser.add_argument("--save", action="store_true", help="Save the extracted data to a file")
    
    args = parser.parse_args()
    
    # Fetch the webpage
    html_content = fetch_google_books_page(args.book_id)
    
    if not html_content:
        print("Failed to fetch the webpage")
        return
    
    # Extract data
    book_data = extract_book_data(html_content)
    
    if not book_data:
        print("Failed to extract book data")
        return
    
    # Print the extracted data
    print("\nExtracted Book Data:")
    pprint(book_data)
    
    # Save the data if requested
    if args.save:
        filename = f"google_books_web_{args.book_id}.json"
        save_data(book_data, filename)

if __name__ == "__main__":
    main() 