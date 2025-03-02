#!/usr/bin/env python3
"""
Script to extract top reviews from Goodreads book pages.
Uses Playwright to handle dynamic content loading and extracts structured review data.
"""

import os
import json
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

import re
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

# Default URL for Pride and Prejudice
DEFAULT_URL = "https://www.goodreads.com/book/show/1885.Pride_and_Prejudice"
MIN_REVIEW_LENGTH = 100  # Minimum word count for reviews
MAX_REVIEWS = 10  # Maximum number of reviews to extract
DEFAULT_SCROLL_DELAY = 2  # Default delay between scrolls in seconds
DEFAULT_SCROLL_COUNT = 3  # Default number of scrolls


def setup_argparse() -> argparse.Namespace:
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(description="Extract top reviews from a Goodreads book page")
    parser.add_argument(
        "--url", 
        type=str, 
        default=DEFAULT_URL,
        help=f"URL of the Goodreads book page (default: {DEFAULT_URL})"
    )
    parser.add_argument(
        "--min-words", 
        type=int, 
        default=MIN_REVIEW_LENGTH,
        help=f"Minimum word count for reviews (default: {MIN_REVIEW_LENGTH})"
    )
    parser.add_argument(
        "--max-reviews", 
        type=int, 
        default=MAX_REVIEWS,
        help=f"Maximum number of reviews to extract (default: {MAX_REVIEWS})"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="goodreads_reviews.json",
        help="Output file path (default: goodreads_reviews.json)"
    )
    parser.add_argument(
        "--format", 
        type=str, 
        choices=["json", "csv"], 
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run browser in visible mode for debugging"
    )
    parser.add_argument(
        "--scroll-delay",
        type=float,
        default=DEFAULT_SCROLL_DELAY,
        help=f"Delay between scrolls in seconds (default: {DEFAULT_SCROLL_DELAY})"
    )
    parser.add_argument(
        "--scroll-count",
        type=int,
        default=DEFAULT_SCROLL_COUNT,
        help=f"Number of times to scroll down (default: {DEFAULT_SCROLL_COUNT})"
    )
    return parser.parse_args()


def extract_star_rating(rating_element_text: str) -> Optional[float]:
    """Extract numeric star rating from rating text."""
    if not rating_element_text:
        return None
    
    # Extract digits and decimal points from the rating text
    match = re.search(r'(\d+(\.\d+)?)', rating_element_text)
    if match:
        return float(match.group(1))
    return None


def count_words(text: str) -> int:
    """Count the number of words in a text."""
    if not text:
        return 0
    return len(text.split())


def extract_reviews(page: Page, min_words: int, max_reviews: int, scroll_delay: float, scroll_count: int) -> List[Dict[str, Any]]:
    """
    Extract reviews from the Goodreads page.
    
    Args:
        page: Playwright page object
        min_words: Minimum word count for reviews
        max_reviews: Maximum number of reviews to extract
        scroll_delay: Delay between scrolls in seconds
        scroll_count: Number of times to scroll down
        
    Returns:
        List of review dictionaries
    """
    reviews = []
    
    # Wait for the reviews section to load
    try:
        page.wait_for_selector('div[data-testid="reviewsList"]', timeout=10000)
    except PlaywrightTimeoutError:
        print("Timeout waiting for reviews section to load")
        return reviews
    
    # Scroll down to load more reviews
    print(f"Scrolling {scroll_count} times with {scroll_delay} second delay between scrolls")
    for i in range(scroll_count):
        page.evaluate("window.scrollBy(0, 1000)")
        print(f"Scroll {i+1}/{scroll_count} completed")
        time.sleep(scroll_delay)  # Wait for content to load
    
    # Extract review elements
    review_elements = page.query_selector_all('div[data-testid="reviewsList"] > div')
    print(f"Found {len(review_elements)} review elements")
    
    for review_element in review_elements:
        if len(reviews) >= max_reviews:
            break
            
        try:
            # Extract username
            username_element = review_element.query_selector('span[data-testid="reviewer"] a')
            if not username_element:
                continue
            username = username_element.inner_text().strip()
            
            # Extract rating
            rating_element = review_element.query_selector('span[data-testid="rating"]')
            rating = None
            if rating_element:
                rating_text = rating_element.get_attribute('aria-label')
                rating = extract_star_rating(rating_text)
            
            # Extract review text
            review_text_element = review_element.query_selector('div[data-testid="reviewText"]')
            if not review_text_element:
                continue
            review_text = review_text_element.inner_text().strip()
            
            # Check if review meets minimum word count
            word_count = count_words(review_text)
            if word_count < min_words:
                print(f"Skipping review by {username} - only {word_count} words (minimum: {min_words})")
                continue
            
            # Extract date (if available)
            date_element = review_element.query_selector('span[data-testid="reviewDate"]')
            review_date = date_element.inner_text().strip() if date_element else None
            
            # Add review to list
            reviews.append({
                'username': username,
                'rating': rating,
                'text': review_text,
                'date': review_date,
                'word_count': word_count
            })
            print(f"Added review by {username} ({word_count} words)")
            
        except Exception as e:
            print(f"Error extracting review: {e}")
            continue
    
    return reviews


def save_to_json(reviews: List[Dict[str, Any]], output_path: str) -> None:
    """Save reviews to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'review_count': len(reviews)
            },
            'reviews': reviews
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(reviews)} reviews to {output_path}")


def save_to_csv(reviews: List[Dict[str, Any]], output_path: str) -> None:
    """Save reviews to a CSV file."""
    import csv
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['username', 'rating', 'text', 'date', 'word_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for review in reviews:
            writer.writerow(review)
    print(f"Saved {len(reviews)} reviews to {output_path}")


def main():
    """Main function to extract and save Goodreads reviews."""
    args = setup_argparse()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Use Playwright to navigate to the page and extract reviews
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"Navigating to {args.url}")
            page.goto(args.url, wait_until="domcontentloaded")
            
            # Wait for page to load
            page.wait_for_selector('h1[data-testid="bookTitle"]', timeout=10000)
            book_title = page.query_selector('h1[data-testid="bookTitle"]').inner_text().strip()
            print(f"Extracting reviews for: {book_title}")
            
            # Extract reviews
            reviews = extract_reviews(
                page, 
                args.min_words, 
                args.max_reviews,
                args.scroll_delay,
                args.scroll_count
            )
            print(f"Extracted {len(reviews)} reviews")
            
            # Save reviews to file
            if args.format.lower() == 'json':
                save_to_json(reviews, args.output)
            else:
                save_to_csv(reviews, args.output)
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main() 