import json
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

def extract_reviews_from_html(html_file):
    """Extract reviews from a Goodreads HTML file."""
    print(f"Reading HTML file: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        print(f"HTML file size: {len(html_content)} bytes")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all review containers
    review_containers = soup.find_all('div', {'class': 'friendReviews elementListBrown'})
    print(f"Found {len(review_containers)} review sections")
    
    reviews = []
    
    for container in review_containers:
        try:
            # Each container has a section that contains the actual review
            review_div = container.find('div', {'class': 'review'})
            if not review_div:
                print("No review div found in container")
                continue
                
            # Extract reviewer name
            reviewer_elem = review_div.find('span', {'itemprop': 'author'})
            if reviewer_elem and reviewer_elem.find('a', {'class': 'user'}):
                reviewer = reviewer_elem.find('a', {'class': 'user'}).text.strip()
            else:
                print("No reviewer found")
                reviewer = "Anonymous"
            
            # Extract rating
            rating_elem = review_div.find('span', {'class': 'staticStars'})
            if rating_elem:
                rating_text = rating_elem.get('title')
                if rating_text == 'it was amazing':
                    rating = 5
                elif rating_text == 'really liked it':
                    rating = 4
                elif rating_text == 'liked it':
                    rating = 3
                elif rating_text == 'it was ok':
                    rating = 2
                elif rating_text == 'did not like it':
                    rating = 1
                else:
                    rating = None
            else:
                print("No rating found")
                rating = None
            
            # Extract date
            date_elem = review_div.find('a', {'class': 'reviewDate'})
            if date_elem:
                date = date_elem.text.strip()
            else:
                print("No date found")
                date = None
            
            # Extract review text - first try to find the expanded text
            review_text_elem = review_div.find('span', {'id': re.compile(r'freeText\d+'), 'style': 'display:none'})
            
            # If expanded text not found, try the visible text
            if not review_text_elem:
                review_text_elem = review_div.find('span', {'id': re.compile(r'freeTextContainer\d+')})
            
            if review_text_elem:
                review_text = review_text_elem.text.strip()
            else:
                print("No review text found")
                review_text = None
            
            # Extract likes count
            likes_elem = review_div.find('span', {'class': 'likesCount'})
            if likes_elem:
                likes_text = likes_elem.text.strip()
                # Extract number from text like "1040 likes"
                likes_match = re.search(r'(\d+)', likes_text)
                if likes_match:
                    likes = int(likes_match.group(1))
                else:
                    likes = 0
            else:
                print("No likes found")
                likes = 0
            
            # Calculate word count to filter for reasonable length
            word_count = len(review_text.split()) if review_text else 0
            
            # Only add reviews that have both a reviewer and reasonable text length
            if reviewer and review_text and word_count >= 50:  # Lowered threshold to 50 words
                reviews.append({
                    'reviewer': reviewer,
                    'rating': rating,
                    'date': date,
                    'text': review_text,
                    'likes': likes,
                    'word_count': word_count
                })
                print(f"Added review by {reviewer} with {word_count} words and {likes} likes")
            else:
                print(f"Skipped review: reviewer={reviewer}, text_length={word_count}")
                
        except Exception as e:
            print(f"Error extracting review: {e}")
    
    # Sort reviews by likes (most helpful first)
    reviews = sorted(reviews, key=lambda x: x['likes'], reverse=True)
    
    # Take only the top 10 reviews
    top_reviews = reviews[:10]
    
    print(f"Extracted {len(reviews)} total reviews")
    print(f"Selected {len(top_reviews)} top reviews by likes")
    return top_reviews

def save_reviews_to_json(reviews, output_file):
    """Save reviews to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'extraction_date': datetime.now().isoformat(),
                'review_count': len(reviews)
            },
            'reviews': reviews
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(reviews)} reviews to {output_file}")

def save_reviews_to_csv(reviews, output_file):
    """Save reviews to a CSV file."""
    df = pd.DataFrame(reviews)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Saved {len(reviews)} reviews to {output_file}")

if __name__ == "__main__":
    html_file = "goodreads_reviews.html"  # Make sure the HTML is saved to this file
    book_id = "1885"  # Pride and Prejudice
    
    reviews = extract_reviews_from_html(html_file)
    
    # Save reviews to JSON and CSV
    json_output = f"reviews_{book_id}.json"
    csv_output = f"reviews_{book_id}.csv"
    
    save_reviews_to_json(reviews, json_output)
    save_reviews_to_csv(reviews, csv_output)