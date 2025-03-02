#!/usr/bin/env python3
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

# Import our custom modules
from extract_amazon_reviews import (
    generate_amazon_reviews_url,
    fetch_amazon_page,
    extract_reviews_from_amazon_html,
    save_reviews_to_json
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_asin_from_url(url):
    """Extract ASIN from Amazon URL"""
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if it's an Amazon URL
        if 'amazon.com' not in parsed_url.netloc:
            logger.warning(f"Not an Amazon URL: {url}")
            return None
        
        # Try to extract from path
        path_parts = parsed_url.path.split('/')
        
        # Look for dp/ASIN pattern
        if 'dp' in path_parts:
            dp_index = path_parts.index('dp')
            if dp_index + 1 < len(path_parts) and path_parts[dp_index + 1]:
                return path_parts[dp_index + 1]
        
        # Look for gp/product/ASIN pattern
        if 'gp' in path_parts and 'product' in path_parts:
            product_index = path_parts.index('product')
            if product_index + 1 < len(path_parts) and path_parts[product_index + 1]:
                return path_parts[product_index + 1]
        
        # Try to extract from query parameters
        query_params = parse_qs(parsed_url.query)
        if 'ASIN' in query_params:
            return query_params['ASIN'][0]
        
        # If all else fails, look for any 10-character alphanumeric string in the path
        # (Amazon ASINs are typically 10 characters)
        import re
        asin_match = re.search(r'/([A-Z0-9]{10})(?:/|\?|$)', parsed_url.path)
        if asin_match:
            return asin_match.group(1)
        
        logger.warning(f"Could not extract ASIN from URL: {url}")
        return None
    
    except Exception as e:
        logger.error(f"Error extracting ASIN from URL {url}: {e}")
        return None

def test_book(book_info, min_words=50, max_reviews=5, analyze_emotions=False):
    """Test Amazon review extraction for a single book"""
    book_title = book_info.get('title', 'Unknown Book')
    amazon_url = book_info.get('amazon_url', '')
    
    logger.info(f"Testing Amazon review extraction for: {book_title}")
    logger.info(f"Amazon URL: {amazon_url}")
    
    # Extract ASIN from URL
    asin = extract_asin_from_url(amazon_url)
    if not asin:
        logger.error(f"Failed to extract ASIN from URL: {amazon_url}")
        return False
    
    logger.info(f"Extracted ASIN: {asin}")
    
    # Generate reviews URL
    reviews_url = generate_amazon_reviews_url(asin)
    logger.info(f"Generated reviews URL: {reviews_url}")
    
    # Fetch the reviews page
    html_content = fetch_amazon_page(reviews_url)
    if not html_content:
        logger.error(f"Failed to fetch reviews page for {book_title}")
        return False
    
    # Save the HTML for debugging
    debug_file = f"amazon_reviews_{asin}_debug.html"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Saved raw HTML to {debug_file} for debugging")
    
    # Extract reviews
    reviews = extract_reviews_from_amazon_html(html_content, min_words=min_words, max_reviews=max_reviews)
    if not reviews:
        logger.error(f"Failed to extract reviews for {book_title}")
        return False
    
    logger.info(f"Successfully extracted {len(reviews)} reviews for {book_title}")
    
    # Save reviews to JSON
    output_file = f"amazon_reviews_{asin}.json"
    save_reviews_to_json(reviews, output_file, book_title, amazon_url)
    logger.info(f"Saved reviews to {output_file}")
    
    # Analyze emotions (if enabled)
    if analyze_emotions:
        try:
            from amazon_emotional_analysis import enhance_reviews_with_emotions
            enhanced_reviews = enhance_reviews_with_emotions(reviews)
            if enhanced_reviews:
                output_file = f"amazon_reviews_{asin}_with_emotions.json"
                save_reviews_to_json(enhanced_reviews, output_file, book_title, amazon_url)
                logger.info(f"Saved enhanced reviews with emotions to {output_file}")
        except Exception as e:
            logger.error(f"Error analyzing emotions: {e}")
    
    return True

def main():
    """Main function to test Amazon review extraction"""
    parser = argparse.ArgumentParser(description='Test Amazon review extraction')
    parser.add_argument('--min-words', type=int, default=50, help='Minimum number of words for a review')
    parser.add_argument('--max-reviews', type=int, default=5, help='Maximum number of reviews to extract')
    parser.add_argument('--analyze-emotions', action='store_true', help='Analyze emotions in reviews')
    args = parser.parse_args()
    
    logger.info("Starting Amazon review extraction tests")
    
    try:
        # Load test books
        with open('test_book.json', 'r') as f:
            test_books = json.load(f)
        
        success_count = 0
        for book in test_books:
            if test_book(book, min_words=args.min_words, max_reviews=args.max_reviews, analyze_emotions=args.analyze_emotions):
                success_count += 1
        
        logger.info(f"Tests completed. {success_count}/{len(test_books)} books processed successfully.")
        
        if success_count == 0:
            logger.error("All tests failed.")
            return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit(main())