#!/usr/bin/env python3
import json
import re
import os
import sys
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
import argparse
import requests
from urllib.parse import urlparse, parse_qs
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("amazon_scraping.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import TextBlob for sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logger.warning("TextBlob not available. Sentiment analysis will be disabled.")

# User agent list for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

def get_random_user_agent():
    """Return a random user agent from the list."""
    return random.choice(USER_AGENTS)

def count_words(text):
    """Count the number of words in a text."""
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Split by whitespace and count
    return len(re.findall(r'\b\w+\b', text))

def analyze_sentiment(text):
    """
    Analyze the sentiment of a text using TextBlob.
    Returns a dictionary with polarity and subjectivity scores.
    """
    if not TEXTBLOB_AVAILABLE:
        return None
    
    try:
        analysis = TextBlob(text)
        return {
            'polarity': round(analysis.sentiment.polarity, 2),
            'subjectivity': round(analysis.sentiment.subjectivity, 2)
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return None

def extract_amazon_id_from_url(url):
    """Extract the Amazon product ID (ASIN) from a URL."""
    # Try to extract from path
    path_match = re.search(r'/dp/([A-Z0-9]{10})(?:/|$)', url)
    if path_match:
        return path_match.group(1)
    
    # Try to extract from query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'ASIN' in query_params:
        return query_params['ASIN'][0]
    
    return None

def get_amazon_url_from_goodreads(goodreads_html_file):
    """
    Extract Amazon URL from a Goodreads book page HTML file.
    Returns the Amazon URL if found, None otherwise.
    """
    try:
        with open(goodreads_html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for the "Buy on Amazon" button or link
        amazon_links = soup.select('a[href*="amazon.com"]')
        
        for link in amazon_links:
            href = link.get('href', '')
            if 'amazon.com' in href:
                # Extract the actual Amazon URL if it's in a redirect
                if 'goodreads.com/buy/redir' in href:
                    parsed_url = urlparse(href)
                    query_params = parse_qs(parsed_url.query)
                    if 'url' in query_params:
                        return query_params['url'][0]
                return href
        
        logger.warning("No Amazon link found in the Goodreads page.")
        return None
    
    except Exception as e:
        logger.error(f"Error extracting Amazon URL from Goodreads: {e}")
        return None

def fetch_amazon_page(url, max_retries=3, delay=2):
    """
    Fetch an Amazon page with retries and random user agent rotation.
    Returns the HTML content if successful, None otherwise.
    """
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching Amazon page: {url} (Attempt {attempt+1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Successfully fetched Amazon page ({len(response.text)} bytes)")
                return response.text
            
            logger.warning(f"Failed to fetch Amazon page: HTTP {response.status_code}")
            
            # Add delay between retries
            if attempt < max_retries - 1:
                sleep_time = delay * (attempt + 1)
                logger.info(f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
        
        except Exception as e:
            logger.error(f"Error fetching Amazon page: {e}")
            if attempt < max_retries - 1:
                sleep_time = delay * (attempt + 1)
                logger.info(f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
    
    logger.error(f"Failed to fetch Amazon page after {max_retries} attempts")
    return None

def generate_amazon_reviews_url(asin):
    """
    Generate the URL for Amazon reviews page based on the ASIN.
    
    Args:
        asin: Amazon Standard Identification Number
        
    Returns:
        str: URL to the Amazon reviews page
    """
    if not asin:
        logger.error("No ASIN provided")
        return None
    
    # Format: https://www.amazon.com/product-reviews/[ASIN]/
    return f"https://www.amazon.com/product-reviews/{asin}/"

def get_amazon_reviews_url(product_url):
    """
    Convert a product URL to a reviews URL.
    """
    asin = extract_amazon_id_from_url(product_url)
    if not asin:
        logger.error(f"Could not extract ASIN from URL: {product_url}")
        return None
    
    # Use the generate_amazon_reviews_url function
    return generate_amazon_reviews_url(asin)

def extract_reviews_from_amazon_html(html_content, min_words=50, max_reviews=10):
    """
    Extract reviews from Amazon HTML content.
    
    Args:
        html_content: HTML content of the Amazon reviews page
        min_words: Minimum number of words for a review to be considered
        max_reviews: Maximum number of reviews to return
        
    Returns:
        list: List of review dictionaries
    """
    if not html_content:
        logger.error("No HTML content provided")
        return []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Save the HTML for debugging
        with open("amazon_debug.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Saved HTML content to amazon_debug.html for debugging")
        
        # Try different selectors for review containers
        review_elements = []
        
        # Try the standard selector
        review_elements = soup.select('div[data-hook="review"]')
        
        # If that doesn't work, try alternative selectors
        if not review_elements:
            review_elements = soup.select('.review')
        
        if not review_elements:
            review_elements = soup.select('.a-section.review')
            
        if not review_elements:
            review_elements = soup.select('.a-section.celwidget')
        
        if not review_elements:
            # Try to find reviews by looking for rating elements first
            rating_elements = soup.select('i[data-hook="review-star-rating"]')
            if rating_elements:
                # For each rating element, find its parent review container
                for rating_element in rating_elements:
                    parent = rating_element.find_parent('div', class_='a-section')
                    if parent and parent not in review_elements:
                        review_elements.append(parent)
        
        if not review_elements:
            logger.warning("No reviews found in the HTML. Check if the HTML structure has changed.")
            return []
        
        logger.info(f"Found {len(review_elements)} reviews in the HTML.")
        
        reviews = []
        for i, review_element in enumerate(review_elements):
            try:
                # Extract reviewer name - try different selectors
                reviewer = "Anonymous"
                reviewer_selectors = [
                    'span.a-profile-name',
                    '.a-profile-name',
                    '.a-row .a-profile-name',
                    'a[data-hook="review-author"] .a-profile-name'
                ]
                
                for selector in reviewer_selectors:
                    reviewer_element = review_element.select_one(selector)
                    if reviewer_element:
                        reviewer = reviewer_element.text.strip()
                        break
                
                # Extract rating - try different selectors
                rating = 0
                rating_selectors = [
                    'i[data-hook="review-star-rating"] span.a-icon-alt',
                    'i[data-hook="review-star-rating"]',
                    '.a-icon-star .a-icon-alt',
                    '.a-icon-star'
                ]
                
                for selector in rating_selectors:
                    rating_element = review_element.select_one(selector)
                    if rating_element:
                        if 'alt' in rating_element.attrs:
                            rating_text = rating_element['alt']
                        elif rating_element.has_attr('title'):
                            rating_text = rating_element['title']
                        else:
                            rating_text = rating_element.text.strip()
                        
                        rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                            break
                
                # Extract review title - try different selectors
                title = ""
                title_selectors = [
                    'a[data-hook="review-title"] span',
                    '[data-hook="review-title"]',
                    '.review-title',
                    '.review-title span'
                ]
                
                for selector in title_selectors:
                    title_element = review_element.select_one(selector)
                    if title_element:
                        title = title_element.text.strip()
                        break
                
                # Extract review date - try different selectors
                date = "Unknown date"
                date_selectors = [
                    'span[data-hook="review-date"]',
                    '.review-date',
                    '.a-color-secondary[data-hook="review-date"]'
                ]
                
                for selector in date_selectors:
                    date_element = review_element.select_one(selector)
                    if date_element:
                        date = date_element.text.strip()
                        break
                
                # Extract review text - try different selectors
                review_text = ""
                text_selectors = [
                    'span[data-hook="review-body"] span',
                    '[data-hook="review-body"]',
                    '.review-text',
                    '.review-text-content span',
                    '.a-expander-content'
                ]
                
                for selector in text_selectors:
                    text_element = review_element.select_one(selector)
                    if text_element:
                        review_text = text_element.text.strip()
                        break
                
                # Extract helpful votes - try different selectors
                helpful_votes = 0
                votes_selectors = [
                    'span[data-hook="helpful-vote-statement"]',
                    '.cr-vote-text',
                    '.a-size-base[data-hook="helpful-vote-statement"]'
                ]
                
                for selector in votes_selectors:
                    votes_element = review_element.select_one(selector)
                    if votes_element:
                        votes_text = votes_element.text.strip()
                        votes_match = re.search(r'(\d+)', votes_text)
                        if votes_match:
                            helpful_votes = int(votes_match.group(1))
                            break
                
                # Count words in review
                word_count = count_words(review_text)
                
                # Only include reviews with at least min_words
                if word_count >= min_words:
                    review_data = {
                        'reviewer': reviewer,
                        'rating': rating,
                        'title': title,
                        'text': review_text,
                        'date': date,
                        'helpful_votes': helpful_votes,
                        'word_count': word_count
                    }
                    
                    # Add sentiment analysis if available
                    if TEXTBLOB_AVAILABLE:
                        sentiment = analyze_sentiment(review_text)
                        if sentiment:
                            review_data['sentiment'] = sentiment
                    
                    reviews.append(review_data)
                    logger.info(f"Extracted review {i+1}/{len(review_elements)} from {reviewer} ({word_count} words, {rating}/5 stars)")
                else:
                    logger.info(f"Skipped review {i+1}/{len(review_elements)} from {reviewer} - too short ({word_count} words)")
            
            except Exception as e:
                logger.error(f"Error extracting review {i+1}: {e}")
                logger.error(f"Review HTML: {review_element}")
        
        if not reviews:
            logger.warning("No reviews matched your criteria.")
            return []
        
        logger.info(f"Successfully extracted {len(reviews)} reviews that match your criteria.")
        
        # Sort reviews by helpful votes (descending)
        reviews.sort(key=lambda x: x['helpful_votes'], reverse=True)
        
        # Return top N reviews
        return reviews[:max_reviews]
    
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return []

def save_reviews_to_json(reviews, output_file, book_title=None, amazon_url=None):
    """
    Save reviews to a JSON file.
    
    Args:
        reviews: List of review dictionaries
        output_file: Path to the output JSON file
        book_title: Title of the book (optional)
        amazon_url: Amazon URL of the book (optional)
        
    Returns:
        str: Path to the saved file, or None if an error occurred
    """
    # Extract book_id from output_file if not provided
    book_id = None
    if amazon_url:
        book_id = extract_amazon_id_from_url(amazon_url)
    
    if not book_id and output_file:
        # Try to extract from the output filename
        match = re.search(r'amazon_reviews_([A-Z0-9]+)\.json', output_file)
        if match:
            book_id = match.group(1)
    
    if not book_id:
        book_id = "unknown"
    
    data = {
        'metadata': {
            'extraction_date': datetime.now().isoformat(),
            'review_count': len(reviews),
            'source': 'amazon',
            'book_id': book_id
        },
        'reviews': reviews
    }
    
    # Add book title if provided
    if book_title:
        data['metadata']['book_title'] = book_title
    
    # Add Amazon URL if provided
    if amazon_url:
        data['metadata']['amazon_url'] = amazon_url
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(reviews)} reviews to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error saving reviews to JSON: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Extract reviews from Amazon for a book')
    parser.add_argument('--goodreads-html', help='Path to the Goodreads HTML file to extract Amazon link from')
    parser.add_argument('--amazon-url', help='Direct Amazon product URL (alternative to goodreads-html)')
    parser.add_argument('--output', help='Output JSON file (default: amazon_reviews_<ASIN>.json)')
    parser.add_argument('--min-words', type=int, default=50, help='Minimum number of words for a review')
    parser.add_argument('--max-reviews', type=int, default=10, help='Maximum number of reviews to extract')
    parser.add_argument('--book-id', help='Book ID for metadata (optional)')
    
    args = parser.parse_args()
    
    # Check if we have either a Goodreads HTML file or an Amazon URL
    if not args.goodreads_html and not args.amazon_url:
        logger.error("Either --goodreads-html or --amazon-url must be provided")
        sys.exit(1)
    
    # Get Amazon URL
    amazon_url = None
    if args.amazon_url:
        amazon_url = args.amazon_url
    elif args.goodreads_html:
        amazon_url = get_amazon_url_from_goodreads(args.goodreads_html)
        if not amazon_url:
            logger.error("Could not find Amazon URL in the Goodreads HTML file")
            sys.exit(1)
    
    # Get the reviews URL
    reviews_url = get_amazon_reviews_url(amazon_url)
    if not reviews_url:
        logger.error("Could not generate Amazon reviews URL")
        sys.exit(1)
    
    # Fetch the reviews page
    html_content = fetch_amazon_page(reviews_url)
    if not html_content:
        logger.error("Failed to fetch Amazon reviews page")
        sys.exit(1)
    
    # Extract the ASIN for the book ID if not provided
    book_id = args.book_id
    if not book_id:
        book_id = extract_amazon_id_from_url(amazon_url) or "unknown"
    
    # Extract reviews
    reviews = extract_reviews_from_amazon_html(
        html_content,
        min_words=args.min_words,
        max_reviews=args.max_reviews
    )
    
    if reviews:
        # Save reviews to JSON
        output_file = args.output or f"amazon_reviews_{book_id}.json"
        save_reviews_to_json(reviews, output_file, book_title=None, amazon_url=amazon_url)
    else:
        logger.error("No reviews were extracted")
        sys.exit(1)

if __name__ == '__main__':
    main() 