#!/usr/bin/env python3
import json
import re
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import argparse

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

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
    Returns a tuple of (polarity, subjectivity) where:
    - polarity is between -1 (negative) and 1 (positive)
    - subjectivity is between 0 (objective) and 1 (subjective)
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
        print(f"Error analyzing sentiment: {e}")
        return None

def extract_reviews(html_file, min_words=100, max_reviews=10, min_rating=0, analyze_sentiments=False):
    """
    Extract reviews from Goodreads HTML file.
    
    Args:
        html_file (str): Path to the HTML file
        min_words (int): Minimum number of words for a review to be considered
        max_reviews (int): Maximum number of reviews to return
        min_rating (int): Minimum rating (1-5) to include
        analyze_sentiments (bool): Whether to analyze sentiment of reviews
        
    Returns:
        list: List of review dictionaries
    """
    print(f"Extracting reviews from {html_file}...")
    
    # Check if file exists
    if not os.path.exists(html_file):
        print(f"Error: File {html_file} not found.")
        return []
    
    try:
        # Read the HTML file
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all review articles
        review_elements = soup.find_all('article', class_='ReviewCard')
        
        if not review_elements:
            print("No reviews found in the HTML. Check if the HTML structure has changed.")
            return []
        
        print(f"Found {len(review_elements)} reviews in the HTML.")
        
        reviews = []
        for i, review_element in enumerate(review_elements):
            try:
                # Extract username
                username_element = review_element.select_one('.ReviewerProfile__name a')
                username = username_element.text.strip() if username_element else "Unknown"
                
                # Extract rating
                rating_stars = review_element.select('.RatingStar--small')
                rating = len(rating_stars) if rating_stars else 0
                
                # Skip reviews with rating below minimum
                if rating < min_rating:
                    print(f"Skipped review {i+1}/{len(review_elements)} from {username} - rating too low ({rating}/5)")
                    continue
                
                # Extract review text
                review_text_element = review_element.select_one('.TruncatedContent__text')
                review_text = ""
                if review_text_element:
                    # Get all text content
                    review_text = review_text_element.get_text(separator=' ', strip=True)
                
                # Extract likes count
                likes_element = review_element.select_one('.SocialFooter__statsContainer button')
                likes_text = likes_element.text.strip() if likes_element else "0 likes"
                likes_count = int(re.search(r'(\d+)', likes_text).group(1)) if re.search(r'(\d+)', likes_text) else 0
                
                # Extract date - try different selectors
                date = "Unknown date"
                date_element = review_element.select_one('.ReviewText__content + .Text__body3 a')
                if date_element:
                    date = date_element.text.strip()
                else:
                    # Try alternative selector
                    date_element = review_element.select_one('.ShelfStatus + span a')
                    if date_element:
                        date = date_element.text.strip()
                
                # Count words in review
                word_count = count_words(review_text)
                
                # Only include reviews with at least min_words
                if word_count >= min_words:
                    review_data = {
                        'username': username,
                        'rating': rating,
                        'text': review_text,
                        'likes': likes_count,
                        'date': date,
                        'word_count': word_count
                    }
                    
                    # Add sentiment analysis if requested
                    if analyze_sentiments and TEXTBLOB_AVAILABLE:
                        sentiment = analyze_sentiment(review_text)
                        if sentiment:
                            review_data['sentiment'] = sentiment
                    
                    reviews.append(review_data)
                    print(f"Extracted review {i+1}/{len(review_elements)} from {username} ({word_count} words, {rating}/5 stars)")
                else:
                    print(f"Skipped review {i+1}/{len(review_elements)} from {username} - too short ({word_count} words)")
            except Exception as e:
                print(f"Error extracting review {i+1}: {e}")
        
        if not reviews:
            print("No reviews matched your criteria.")
            return []
        
        print(f"Successfully extracted {len(reviews)} reviews that match your criteria.")
        
        # Sort reviews by likes count (descending)
        reviews.sort(key=lambda x: x['likes'], reverse=True)
        
        # Return top N reviews
        return reviews[:max_reviews]
    
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return []

def save_reviews_to_json(reviews, output_file):
    """Save reviews to a JSON file."""
    data = {
        'metadata': {
            'extraction_date': datetime.now().isoformat(),
            'review_count': len(reviews)
        },
        'reviews': reviews
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(reviews)} reviews to {output_file}")
    except Exception as e:
        print(f"Error saving reviews to JSON: {e}")

def main():
    parser = argparse.ArgumentParser(description='Extract reviews from Goodreads HTML file')
    parser.add_argument('--html', default='goodreads_page.html', help='Path to the HTML file')
    parser.add_argument('--output', default='goodreads_reviews.json', help='Output JSON file')
    parser.add_argument('--min-words', type=int, default=100, help='Minimum number of words for a review')
    parser.add_argument('--max-reviews', type=int, default=10, help='Maximum number of reviews to extract')
    parser.add_argument('--min-rating', type=int, default=0, choices=range(0, 6), 
                        help='Minimum rating (1-5) to include, 0 for any rating')
    parser.add_argument('--sort', choices=['likes', 'rating', 'date', 'length'], default='likes',
                        help='Sort reviews by this field')
    parser.add_argument('--sentiment', action='store_true', help='Include sentiment analysis (requires TextBlob)')
    
    args = parser.parse_args()
    
    # Check if TextBlob is available when sentiment analysis is requested
    if args.sentiment and not TEXTBLOB_AVAILABLE:
        print("Warning: TextBlob is not installed. Sentiment analysis will be skipped.")
        print("To install TextBlob, run: pip install textblob")
        print("Then run: python -m textblob.download_corpora")
        args.sentiment = False
    
    reviews = extract_reviews(
        args.html, 
        args.min_words, 
        args.max_reviews, 
        args.min_rating,
        args.sentiment
    )
    
    if reviews:
        # Sort reviews based on the specified field
        if args.sort == 'rating':
            reviews.sort(key=lambda x: x['rating'], reverse=True)
        elif args.sort == 'date':
            # Try to parse dates, but this is complex due to varying formats
            # For simplicity, we'll just sort by the date string
            reviews.sort(key=lambda x: x['date'], reverse=True)
        elif args.sort == 'length':
            reviews.sort(key=lambda x: x['word_count'], reverse=True)
        # Default is 'likes', which is already sorted
        
        save_reviews_to_json(reviews, args.output)
    else:
        print("No reviews were extracted. Check the HTML structure or try a different file.")
        sys.exit(1)

if __name__ == '__main__':
    main() 