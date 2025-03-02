#!/usr/bin/env python3
"""
Enhanced script to scrape data from Google Books webpages.
This script combines the Google Books API and web scraping to get comprehensive book data.
"""

import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup
from pprint import pprint
from pathlib import Path
import re
import time
import random

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_google_books_api(title, author=None):
    """Fetch book information from Google Books API."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    
    query = f"intitle:{title}"
    if author:
        query += f"+inauthor:{author}"
    
    params = {
        'q': query,
        'maxResults': 5
    }
    
    print(f"Fetching data for title: '{title}'" + (f" by author: '{author}'" if author else ""))
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            print("No books found matching the criteria")
            return None
        
        # Get the first result's ID
        volume_id = data['items'][0]['id']
        print(f"\nFound volume ID: {volume_id}")
        
        # Fetch detailed information for this volume
        print(f"Fetching detailed information for this volume...")
        volume_url = f"{base_url}/{volume_id}"
        volume_response = requests.get(volume_url, timeout=10)
        volume_response.raise_for_status()
        volume_data = volume_response.json()
        
        return volume_data
    except requests.RequestException as e:
        print(f"Error fetching data from Google Books API: {e}")
        return None

def fetch_google_books_page(book_id):
    """Fetch the Google Books webpage for a specific book ID."""
    # Try different URL formats
    urls = [
        f"https://www.google.com/books/edition/_/{book_id}?hl=en",
        f"https://books.google.com/books?id={book_id}&hl=en",
        f"https://books.google.com/books/about/?id={book_id}&hl=en"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    
    for url in urls:
        print(f"Trying to fetch Google Books webpage: {url}")
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                print(f"Successfully fetched webpage from: {url}")
                return response.text
        except requests.RequestException as e:
            print(f"Error fetching webpage from {url}: {e}")
    
    print("Failed to fetch Google Books webpage from all attempted URLs")
    return None

def extract_book_data(html_content):
    """Extract book data from the Google Books webpage HTML."""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    book_data = {}
    
    # Save the HTML for debugging
    with open("google_books_debug.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Saved HTML content to google_books_debug.html for debugging")
    
    # Basic book information - try multiple selectors for different page layouts
    try:
        # Title - try different selectors
        title_selectors = [
            'h1.AHFaub',  # Modern layout
            'div.dsBk5c h1',  # Alternative layout
            'h1[itemprop="name"]',  # Schema.org markup
            'h1',  # Generic fallback
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.text.strip():
                book_data['title'] = title_elem.text.strip()
                break
        
        # Author - try different selectors
        author_selectors = [
            'a[href*="inauthor"]',  # Common pattern
            'div.dsBk5c a[href*="inauthor"]',  # Alternative layout
            'span[itemprop="author"]',  # Schema.org markup
            'div.Z4XEye a',  # Modern layout
        ]
        
        for selector in author_selectors:
            author_elems = soup.select(selector)
            if author_elems:
                book_data['authors'] = [author.text.strip() for author in author_elems if author.text.strip()]
                break
        
        # Publisher and publication date
        info_selectors = [
            'div.IQ1z0d',  # Modern layout
            'div.dsBk5c div.IQ1z0d',  # Alternative layout
            'div[itemprop="publisher"]',  # Schema.org markup
        ]
        
        for selector in info_selectors:
            info_elem = soup.select_one(selector)
            if info_elem:
                info_text = info_elem.text.strip()
                # Try to extract publisher
                publisher_match = re.search(r'(?:Publisher|Published by)[:\s]+([^,\n]+)', info_text)
                if publisher_match:
                    book_data['publisher'] = publisher_match.group(1).strip()
                
                # Try to extract publication date
                date_match = re.search(r'(?:Published|Publication date)[:\s]+([^,\n]+\d{4})', info_text)
                if date_match:
                    book_data['published_date'] = date_match.group(1).strip()
                
                # Try to extract page count
                pages_match = re.search(r'(\d+)\s+pages', info_text)
                if pages_match:
                    book_data['page_count'] = int(pages_match.group(1))
                
                break
        
        # ISBN
        isbn_text = soup.find(string=re.compile('ISBN'))
        if isbn_text:
            isbn_parent = isbn_text.find_parent()
            if isbn_parent:
                isbn_row = isbn_parent.find_next_sibling()
                if isbn_row:
                    isbn_match = re.search(r'(\d[\d\-]+\d)', isbn_row.text)
                    if isbn_match:
                        book_data['isbn'] = isbn_match.group(1).replace('-', '')
    
    except Exception as e:
        print(f"Error extracting basic book information: {e}")
    
    # Description
    try:
        description_selectors = [
            'div[itemprop="description"]',  # Schema.org markup
            'div.IiD0ob',  # Modern layout
            'div.dsBk5c div.IiD0ob',  # Alternative layout
        ]
        
        for selector in description_selectors:
            description_elem = soup.select_one(selector)
            if description_elem and description_elem.text.strip():
                book_data['description'] = description_elem.text.strip()
                break
    except Exception as e:
        print(f"Error extracting description: {e}")
    
    # Categories/Genres
    try:
        categories_selectors = [
            'div.dsBk5c a[href*="subject:"]',  # Common pattern
            'a[href*="subject:"]',  # Alternative pattern
            'span[itemprop="genre"]',  # Schema.org markup
        ]
        
        for selector in categories_selectors:
            category_elems = soup.select(selector)
            if category_elems:
                book_data['categories'] = [cat.text.strip() for cat in category_elems if cat.text.strip()]
                break
    except Exception as e:
        print(f"Error extracting categories: {e}")
    
    # Common terms and phrases
    try:
        terms_heading = soup.find(string=lambda text: text and 'Common terms and phrases' in text)
        if terms_heading:
            terms_parent = terms_heading.find_parent()
            if terms_parent:
                terms_section = terms_parent.find_next_sibling()
                if terms_section:
                    terms = [term.text.strip() for term in terms_section.select('a') if term.text.strip()]
                    if terms:
                        book_data['common_terms'] = terms
    except Exception as e:
        print(f"Error extracting common terms: {e}")
    
    # Popular passages
    try:
        passages_heading = soup.find(string=lambda text: text and 'Popular passages' in text)
        if passages_heading:
            passages_parent = passages_heading.find_parent()
            if passages_parent:
                passages = []
                current_elem = passages_parent.find_next_sibling()
                
                while current_elem and not (current_elem.name == 'h2' or current_elem.name == 'h3'):
                    passage_text = current_elem.select_one('.passage-text, div.VfPpkd-EScbFb-JIbuQc')
                    if passage_text:
                        passage_info = current_elem.select_one('.passage-info, div.VfPpkd-EScbFb-LvqzAb')
                        passages.append({
                            'text': passage_text.text.strip(),
                            'info': passage_info.text.strip() if passage_info else None
                        })
                    current_elem = current_elem.find_next_sibling()
                
                if passages:
                    book_data['popular_passages'] = passages
    except Exception as e:
        print(f"Error extracting popular passages: {e}")
    
    # About the author
    try:
        about_author_heading = soup.find(string=lambda text: text and 'About the author' in text)
        if about_author_heading:
            about_parent = about_author_heading.find_parent()
            if about_parent:
                about_section = about_parent.find_next_sibling()
                if about_section and about_section.text.strip():
                    book_data['about_author'] = about_section.text.strip()
    except Exception as e:
        print(f"Error extracting author information: {e}")
    
    # Reviews
    try:
        reviews_heading = soup.find(string=lambda text: text and 'Reviews' in text)
        if reviews_heading:
            reviews_parent = reviews_heading.find_parent()
            if reviews_parent:
                reviews_section = reviews_parent.find_next_sibling()
                if reviews_section:
                    review_elems = reviews_section.select('div.review')
                    if review_elems:
                        reviews = []
                        for review in review_elems:
                            review_text = review.select_one('div.review-text')
                            review_info = review.select_one('div.review-info')
                            if review_text:
                                reviews.append({
                                    'text': review_text.text.strip(),
                                    'info': review_info.text.strip() if review_info else None
                                })
                        if reviews:
                            book_data['reviews'] = reviews
    except Exception as e:
        print(f"Error extracting reviews: {e}")
    
    return book_data

def combine_data(api_data, web_data):
    """Combine data from the API and web scraping."""
    if not api_data:
        return web_data
    if not web_data:
        return api_data
    
    combined_data = {}
    
    # Add API data
    if 'volumeInfo' in api_data:
        volume_info = api_data['volumeInfo']
        combined_data.update({
            'id': api_data.get('id'),
            'title': volume_info.get('title'),
            'subtitle': volume_info.get('subtitle'),
            'authors': volume_info.get('authors'),
            'publisher': volume_info.get('publisher'),
            'publishedDate': volume_info.get('publishedDate'),
            'description': volume_info.get('description'),
            'industryIdentifiers': volume_info.get('industryIdentifiers'),
            'pageCount': volume_info.get('pageCount'),
            'categories': volume_info.get('categories'),
            'averageRating': volume_info.get('averageRating'),
            'ratingsCount': volume_info.get('ratingsCount'),
            'maturityRating': volume_info.get('maturityRating'),
            'language': volume_info.get('language'),
            'previewLink': volume_info.get('previewLink'),
            'infoLink': volume_info.get('infoLink'),
            'canonicalVolumeLink': volume_info.get('canonicalVolumeLink'),
        })
    else:
        combined_data.update(api_data)
    
    # Add web data (overriding API data where web data is more complete)
    if web_data:
        # Only override if web data has values and API data doesn't
        for key, value in web_data.items():
            if value and (key not in combined_data or not combined_data[key]):
                combined_data[key] = value
        
        # Add web-only data
        web_only_keys = ['common_terms', 'popular_passages', 'about_author', 'reviews']
        for key in web_only_keys:
            if key in web_data and web_data[key]:
                combined_data[key] = web_data[key]
    
    return combined_data

def save_data(data, filename):
    """Save the extracted data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Google Books data scraper")
    parser.add_argument("--title", help="Book title to search for")
    parser.add_argument("--author", help="Book author to search for")
    parser.add_argument("--book-id", help="Google Books ID (if already known)")
    parser.add_argument("--save", action="store_true", help="Save the extracted data to a file")
    
    args = parser.parse_args()
    
    if not args.book_id and not args.title:
        print("Error: Either --book-id or --title must be provided")
        return
    
    api_data = None
    book_id = args.book_id
    
    # If no book ID is provided, search for it using the API
    if not book_id:
        api_data = fetch_google_books_api(args.title, args.author)
        if api_data:
            book_id = api_data.get('id')
            if not book_id:
                print("Error: Could not find book ID from API")
                return
    
    # Fetch the webpage
    html_content = fetch_google_books_page(book_id)
    
    if not html_content:
        print("Failed to fetch the webpage")
        if api_data:
            print("\nAPI Data:")
            pprint(api_data)
            if args.save:
                filename = f"google_books_api_{book_id}.json"
                save_data(api_data, filename)
        return
    
    # Extract data from the webpage
    web_data = extract_book_data(html_content)
    
    if not web_data:
        print("Failed to extract book data from webpage")
        if api_data:
            print("\nAPI Data:")
            pprint(api_data)
            if args.save:
                filename = f"google_books_api_{book_id}.json"
                save_data(api_data, filename)
        return
    
    # If we didn't get API data earlier but have a book ID, try to fetch it now
    if not api_data and book_id:
        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                api_data = response.json()
        except Exception as e:
            print(f"Error fetching API data for book ID {book_id}: {e}")
    
    # Combine data from both sources
    combined_data = combine_data(api_data, web_data)
    
    # Print the extracted data
    print("\nExtracted Book Data:")
    pprint(combined_data)
    
    # Save the data if requested
    if args.save:
        filename = f"google_books_combined_{book_id}.json"
        save_data(combined_data, filename)

if __name__ == "__main__":
    main() 