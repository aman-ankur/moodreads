#!/usr/bin/env python3
"""
Script to extract and display the major sections from a Google Books page.
This script focuses on identifying and extracting the structured content sections.
"""

import sys
import requests
from bs4 import BeautifulSoup
import argparse
import re
import time
import random

# Add the project root to the Python path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_google_books_page(url):
    """Fetch the Google Books webpage."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    
    print(f"Fetching Google Books webpage: {url}")
    try:
        # Add a small delay to avoid rate limiting
        time.sleep(random.uniform(1, 2))
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            print(f"Successfully fetched webpage")
            return response.text
        else:
            print(f"Failed to fetch webpage: Status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None

def extract_sections(html_content):
    """Extract major sections from the Google Books webpage HTML."""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = {}
    
    # Save the HTML for debugging
    with open("google_books_debug.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Saved HTML content to google_books_debug.html for debugging")
    
    # Basic book information
    try:
        # Title
        title_elem = soup.select_one('h1')
        if title_elem:
            sections['Title'] = title_elem.text.strip()
        
        # Author
        author_elem = soup.select_one('a[href*="inauthor"]')
        if author_elem:
            sections['Author'] = author_elem.text.strip()
        
        # Publisher and publication info
        publisher_info = []
        publisher_elem = soup.find(string=re.compile('Publisher'))
        if publisher_elem and publisher_elem.find_parent():
            publisher_row = publisher_elem.find_parent().find_next_sibling()
            if publisher_row:
                publisher_info.append(f"Publisher: {publisher_row.text.strip()}")
        
        pub_date_elem = soup.find(string=re.compile('Published'))
        if pub_date_elem and pub_date_elem.find_parent():
            pub_date_row = pub_date_elem.find_parent().find_next_sibling()
            if pub_date_row:
                publisher_info.append(f"Published: {pub_date_row.text.strip()}")
        
        if publisher_info:
            sections['Publication Info'] = publisher_info
        
        # Description
        description_elem = None
        for elem in soup.find_all(['div', 'p']):
            if elem.text and len(elem.text.strip()) > 100 and not elem.find_parent('table'):
                description_elem = elem
                break
        
        if description_elem:
            sections['Description'] = description_elem.text.strip()
    
    except Exception as e:
        print(f"Error extracting basic book information: {e}")
    
    # Table of Contents
    try:
        toc_heading = soup.find(string=lambda text: text and 'Table of Contents' in text)
        if toc_heading:
            toc_parent = toc_heading.find_parent()
            if toc_parent:
                toc_section = toc_parent.find_next_sibling()
                if toc_section:
                    toc_items = []
                    for item in toc_section.find_all(['li', 'tr']):
                        if item.text.strip():
                            toc_items.append(item.text.strip())
                    if toc_items:
                        sections['Table of Contents'] = toc_items
    except Exception as e:
        print(f"Error extracting table of contents: {e}")
    
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
                        sections['Common Terms and Phrases'] = terms
    except Exception as e:
        print(f"Error extracting common terms: {e}")
    
    # About the author
    try:
        about_author_heading = soup.find(string=lambda text: text and 'About the author' in text)
        if about_author_heading:
            about_parent = about_author_heading.find_parent()
            if about_parent:
                about_section = about_parent.find_next_sibling()
                if about_section and about_section.text.strip():
                    sections['About the Author'] = about_section.text.strip()
    except Exception as e:
        print(f"Error extracting author information: {e}")
    
    # Bibliographic information
    try:
        biblio_heading = soup.find(string=lambda text: text and 'Bibliographic information' in text)
        if biblio_heading:
            biblio_parent = biblio_heading.find_parent()
            if biblio_parent:
                biblio_section = biblio_parent.find_next_sibling()
                if biblio_section:
                    biblio_items = []
                    for row in biblio_section.select('tr'):
                        if row.select_one('td') and row.select_one('td:nth-of-type(2)'):
                            key = row.select_one('td').text.strip()
                            value = row.select_one('td:nth-of-type(2)').text.strip()
                            biblio_items.append(f"{key}: {value}")
                    if biblio_items:
                        sections['Bibliographic Information'] = biblio_items
    except Exception as e:
        print(f"Error extracting bibliographic information: {e}")
    
    # Other editions
    try:
        editions_heading = soup.find(string=lambda text: text and 'Other editions' in text)
        if editions_heading:
            editions_parent = editions_heading.find_parent()
            if editions_parent:
                editions_section = editions_parent.find_next_sibling()
                if editions_section:
                    editions = []
                    for edition in editions_section.select('tr'):
                        edition_text = edition.text.strip()
                        if edition_text:
                            editions.append(edition_text)
                    if editions:
                        sections['Other Editions'] = editions
    except Exception as e:
        print(f"Error extracting other editions: {e}")
    
    return sections

def display_sections(sections):
    """Display the extracted sections in a readable format."""
    if not sections:
        print("No sections were extracted.")
        return
    
    print("\n" + "="*50)
    print("MAJOR SECTIONS FROM GOOGLE BOOKS PAGE")
    print("="*50)
    
    for section_name, content in sections.items():
        print(f"\n{section_name.upper()}")
        print("-" * len(section_name))
        
        if isinstance(content, list):
            for item in content:
                print(f"• {item}")
        else:
            # For longer text, limit to first 300 characters with ellipsis
            if len(content) > 300:
                print(f"{content[:300]}...")
            else:
                print(content)
    
    print("\n" + "="*50)

def main():
    parser = argparse.ArgumentParser(description="Extract major sections from a Google Books page")
    parser.add_argument("--url", required=True, help="URL of the Google Books page")
    
    args = parser.parse_args()
    
    # Fetch the webpage
    html_content = fetch_google_books_page(args.url)
    
    if not html_content:
        print("Failed to fetch the webpage")
        return
    
    # Extract sections
    sections = extract_sections(html_content)
    
    if not sections:
        print("Failed to extract sections from the webpage")
        return
    
    # Display the sections
    display_sections(sections)

if __name__ == "__main__":
    main() 