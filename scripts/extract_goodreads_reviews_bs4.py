import re
import requests

def fetch_reviews_page(book_url):
    """
    Fetch the reviews page for a book.
    
    Args:
        book_url (str): URL of the book page
        
    Returns:
        str: HTML content of the reviews page
    """
    try:
        # Extract book ID from URL
        book_id_match = re.search(r'/show/(\d+)', book_url)
        if not book_id_match:
            print(f"Could not extract book ID from URL: {book_url}")
            return None
        
        book_id = book_id_match.group(1)
        
        # Construct reviews URL
        reviews_url = f"https://www.goodreads.com/book/reviews/{book_id}?reviewable_type=Book&language_code=en"
        
        # Fetch reviews page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }
        
        print(f"Fetching reviews from: {reviews_url}")
        response = requests.get(reviews_url, headers=headers)
        response.raise_for_status()
        
        # Save HTML content to a file for debugging
        with open('debug_reviews.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved HTML content to debug_reviews.html for debugging")
        
        return response.text
    
    except Exception as e:
        print(f"Error fetching reviews page: {e}")
        return None 