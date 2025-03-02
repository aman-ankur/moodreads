#!/usr/bin/env python3
import os
import json
import time
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import numpy as np

import anthropic
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_books_emotional_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API keys from environment variables
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class GoogleBooksClient:
    """Client for interacting with Google Books API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Books client.
        
        Args:
            api_key: Google API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google API key not provided and GOOGLE_API_KEY environment variable not set")
        
        self.service = build('books', 'v1', developerKey=self.api_key)
        logger.info("Google Books client initialized")
    
    def search_book(self, query: str, max_results: int = 1) -> List[Dict]:
        """
        Search for books matching the query.
        
        Args:
            query: Search query (title, author, ISBN, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of book data dictionaries
        """
        try:
            response = self.service.volumes().list(
                q=query,
                maxResults=max_results
            ).execute()
            
            if 'items' not in response:
                logger.warning(f"No books found for query: {query}")
                return []
            
            books = []
            for item in response['items']:
                volume_info = item.get('volumeInfo', {})
                book = {
                    'id': item.get('id'),
                    'title': volume_info.get('title', 'Unknown Title'),
                    'authors': volume_info.get('authors', []),
                    'publisher': volume_info.get('publisher'),
                    'published_date': volume_info.get('publishedDate'),
                    'description': volume_info.get('description', ''),
                    'categories': volume_info.get('categories', []),
                    'average_rating': volume_info.get('averageRating'),
                    'ratings_count': volume_info.get('ratingsCount', 0),
                    'isbn': self._extract_isbn(volume_info.get('industryIdentifiers', [])),
                    'page_count': volume_info.get('pageCount'),
                    'language': volume_info.get('language'),
                    'preview_link': volume_info.get('previewLink'),
                    'info_link': volume_info.get('infoLink'),
                    'image_links': volume_info.get('imageLinks', {})
                }
                books.append(book)
            
            logger.info(f"Found {len(books)} books for query: {query}")
            return books
        
        except HttpError as error:
            logger.error(f"Google Books API error: {error}")
            return []
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Get book data by ISBN.
        
        Args:
            isbn: ISBN of the book
            
        Returns:
            Book data dictionary or None if not found
        """
        books = self.search_book(f"isbn:{isbn}")
        return books[0] if books else None
    
    def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        """
        Get book data by Google Books ID.
        
        Args:
            book_id: Google Books ID
            
        Returns:
            Book data dictionary or None if not found
        """
        try:
            response = self.service.volumes().get(volumeId=book_id).execute()
            volume_info = response.get('volumeInfo', {})
            
            book = {
                'id': response.get('id'),
                'title': volume_info.get('title', 'Unknown Title'),
                'authors': volume_info.get('authors', []),
                'publisher': volume_info.get('publisher'),
                'published_date': volume_info.get('publishedDate'),
                'description': volume_info.get('description', ''),
                'categories': volume_info.get('categories', []),
                'average_rating': volume_info.get('averageRating'),
                'ratings_count': volume_info.get('ratingsCount', 0),
                'isbn': self._extract_isbn(volume_info.get('industryIdentifiers', [])),
                'page_count': volume_info.get('pageCount'),
                'language': volume_info.get('language'),
                'preview_link': volume_info.get('previewLink'),
                'info_link': volume_info.get('infoLink'),
                'image_links': volume_info.get('imageLinks', {})
            }
            
            return book
        
        except HttpError as error:
            logger.error(f"Google Books API error: {error}")
            return None
    
    def get_book_reviews(self, book_id: str) -> List[Dict]:
        """
        Get reviews for a book from Google Books.
        
        Note: Google Books API doesn't provide direct access to user reviews.
        This method extracts review snippets from the book data.
        
        Args:
            book_id: Google Books ID
            
        Returns:
            List of review dictionaries
        """
        book = self.get_book_by_id(book_id)
        if not book:
            return []
        
        # Google Books doesn't provide full reviews through the API
        # We can only get review snippets from the searchInfo
        reviews = []
        
        # Try to get review snippets from the book data
        try:
            response = self.service.volumes().get(
                volumeId=book_id, 
                fields="volumeInfo(description,ratingsCount,averageRating),searchInfo"
            ).execute()
            
            # Extract snippet if available
            if 'searchInfo' in response and 'textSnippet' in response['searchInfo']:
                snippet = response['searchInfo']['textSnippet']
                reviews.append({
                    'text': snippet,
                    'rating': book.get('average_rating'),
                    'source': 'Google Books Snippet'
                })
        
        except HttpError as error:
            logger.error(f"Google Books API error: {error}")
        
        return reviews
    
    def _extract_isbn(self, identifiers: List[Dict]) -> Optional[str]:
        """Extract ISBN from industry identifiers."""
        for identifier in identifiers:
            if identifier.get('type') == 'ISBN_13':
                return identifier.get('identifier')
            elif identifier.get('type') == 'ISBN_10':
                return identifier.get('identifier')
        return None


class EmotionalAnalyzer:
    """Analyze emotional content of book descriptions and reviews."""
    
    # Genre to emotion mapping for supplementary emotional signals
    GENRE_EMOTION_MAP = {
        'horror': {'fear': 0.8, 'tension': 0.7, 'dread': 0.6},
        'romance': {'joy': 0.7, 'comfort': 0.6, 'hope': 0.5},
        'thriller': {'tension': 0.8, 'curiosity': 0.7, 'excitement': 0.6},
        'mystery': {'curiosity': 0.8, 'tension': 0.6, 'satisfaction': 0.5},
        'fantasy': {'wonder': 0.8, 'curiosity': 0.6, 'inspiration': 0.5},
        'science fiction': {'wonder': 0.7, 'curiosity': 0.7, 'tension': 0.4},
        'literary fiction': {'reflection': 0.7, 'melancholy': 0.5, 'satisfaction': 0.6},
        'historical fiction': {'reflection': 0.6, 'curiosity': 0.5, 'satisfaction': 0.5},
        'young adult': {'excitement': 0.6, 'hope': 0.5, 'curiosity': 0.5},
        'biography': {'reflection': 0.7, 'inspiration': 0.6, 'satisfaction': 0.5},
        'self-help': {'hope': 0.8, 'inspiration': 0.7, 'comfort': 0.5},
        'comedy': {'joy': 0.8, 'comfort': 0.6, 'satisfaction': 0.5},
        'drama': {'tension': 0.7, 'reflection': 0.6, 'melancholy': 0.5},
        'adventure': {'excitement': 0.8, 'curiosity': 0.6, 'wonder': 0.5},
        'poetry': {'reflection': 0.7, 'melancholy': 0.5, 'wonder': 0.6},
        'classic': {'reflection': 0.7, 'satisfaction': 0.6, 'melancholy': 0.5}
    }
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize the emotional analyzer.
        
        Args:
            use_cache: Whether to use caching for API calls
        """
        if not CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.use_cache = use_cache
        self.cache = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs('cache', exist_ok=True)
        
        # Load cache if it exists
        self._load_cache()
        
        logger.info("Emotional analyzer initialized")
    
    def _load_cache(self):
        """Load cache from file."""
        cache_file = os.path.join('cache', 'emotional_analysis_cache.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cached analyses")
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                self.cache = {}
    
    def _save_cache(self):
        """Save cache to file."""
        cache_file = os.path.join('cache', 'emotional_analysis_cache.json')
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
            logger.info(f"Saved {len(self.cache)} analyses to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def analyze_description(self, description: str) -> Dict:
        """
        Analyze book description for emotional content.
        
        Args:
            description: Book description text
            
        Returns:
            Dictionary with emotional profile, arc, and keywords
        """
        if not description:
            logger.warning("Empty description provided for analysis")
            return self._get_default_analysis()
        
        try:
            # Check cache first
            cache_key = f"desc_{hashlib.md5(description.encode()).hexdigest()}"
            if self.use_cache and cache_key in self.cache:
                logger.info("Using cached description analysis")
                return self.cache[cache_key]
            
            # Prepare prompt for Claude
            prompt = """
            Analyze this book description and extract the emotional content. Return a JSON object with:
            1. "primary_emotions": Array of objects with "emotion" and "intensity" (0-10 scale)
            2. "emotional_arc": Object with beginning, middle, and end emotional states
            3. "unexpected_emotions": Array of emotions that might be unexpected based on the genre
            4. "lasting_impact": Description of the lasting emotional impact
            5. "emotional_keywords": Array of emotional words/phrases from the text
            6. "overall_emotional_profile": Brief summary of the overall emotional profile
            
            Book description:
            """
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.2,
                system="You are an expert literary analyst specializing in emotional analysis of book descriptions. Your task is to extract nuanced emotional signals from descriptions to create comprehensive emotional profiles for books.",
                messages=[
                    {"role": "user", "content": prompt + description}
                ]
            )
            
            # Extract the JSON from the response
            response_text = response.content[0].text
            
            # Find JSON in the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without the markdown code block
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text
            
            # Parse the JSON
            try:
                analysis = json.loads(json_str)
                
                # Cache result
                if self.use_cache:
                    self.cache[cache_key] = analysis
                    self._save_cache()
                
                return analysis
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Claude's response")
                return {"error": "JSON parsing failed", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"Error analyzing description: {e}")
            return self._get_default_analysis()
    
    def analyze_reviews(self, reviews: List[Dict]) -> Dict:
        """
        Analyze book reviews for emotional content.
        
        Args:
            reviews: List of review dictionaries with 'text' field
            
        Returns:
            Dictionary with aggregated emotional analysis
        """
        if not reviews:
            logger.warning("No reviews provided for analysis")
            return self._get_default_analysis()
        
        try:
            # Combine all review texts
            all_review_text = "\n\n".join([f"Review {i+1}:\n{review.get('text', '')}" for i, review in enumerate(reviews)])
            
            # Check cache first
            cache_key = f"reviews_{hashlib.md5(all_review_text.encode()).hexdigest()}"
            if self.use_cache and cache_key in self.cache:
                logger.info("Using cached reviews analysis")
                return self.cache[cache_key]
            
            # Prepare prompt for Claude
            prompt = """
            Below are multiple reviews of a book. Please analyze these reviews collectively to create a comprehensive emotional profile of the book. Extract the following information:

            1. Primary emotions evoked by the book (joy, sadness, tension, comfort, etc.)
            2. Emotional intensity scores (on a scale of 1-10) for each primary emotion
            3. Emotional progression/arc throughout the book (beginning, middle, end)
            4. Unexpected emotional responses mentioned by readers
            5. Lasting emotional impact described by readers
            6. Emotional keywords and phrases from the reviews

            Reviews:
            """
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.2,
                system="You are an expert literary analyst specializing in emotional analysis of book reviews. Your task is to extract nuanced emotional signals from reviews to create comprehensive emotional profiles for books.",
                messages=[
                    {"role": "user", "content": prompt + all_review_text}
                ]
            )
            
            # Extract the JSON from the response
            response_text = response.content[0].text
            
            # Find JSON in the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without the markdown code block
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text
            
            # Parse the JSON
            try:
                analysis = json.loads(json_str)
                
                # Cache result
                if self.use_cache:
                    self.cache[cache_key] = analysis
                    self._save_cache()
                
                return analysis
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Claude's response")
                return {"error": "JSON parsing failed", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"Error analyzing reviews: {e}")
            return self._get_default_analysis()
    
    def extract_genre_emotions(self, genres: List[str]) -> Dict:
        """
        Extract emotional signals from book genres.
        
        Args:
            genres: List of book genres
            
        Returns:
            Dictionary with emotions and their intensities
        """
        if not genres:
            return {}
        
        genre_emotions = {}
        
        for genre in genres:
            genre_lower = genre.lower()
            
            # Check for exact matches
            if genre_lower in self.GENRE_EMOTION_MAP:
                emotions = self.GENRE_EMOTION_MAP[genre_lower]
                for emotion, intensity in emotions.items():
                    if emotion in genre_emotions:
                        genre_emotions[emotion] = max(genre_emotions[emotion], intensity)
                    else:
                        genre_emotions[emotion] = intensity
            else:
                # Check for partial matches
                for known_genre, emotions in self.GENRE_EMOTION_MAP.items():
                    if known_genre in genre_lower or genre_lower in known_genre:
                        for emotion, intensity in emotions.items():
                            # Reduce intensity for partial matches
                            adjusted_intensity = intensity * 0.8
                            if emotion in genre_emotions:
                                genre_emotions[emotion] = max(genre_emotions[emotion], adjusted_intensity)
                            else:
                                genre_emotions[emotion] = adjusted_intensity
        
        return genre_emotions
    
    def create_emotional_profile(self, book: Dict) -> Dict:
        """
        Create a comprehensive emotional profile for a book.
        
        Args:
            book: Book data dictionary with description, reviews, and genres
            
        Returns:
            Dictionary with comprehensive emotional profile
        """
        description = book.get('description', '')
        reviews = book.get('reviews', [])
        genres = book.get('categories', [])
        
        # Analyze description
        description_analysis = self.analyze_description(description)
        
        # Analyze reviews
        reviews_analysis = self.analyze_reviews(reviews)
        
        # Extract genre emotions
        genre_emotions = self.extract_genre_emotions(genres)
        
        # Combine all emotional signals
        combined_analysis = self._combine_emotional_signals(
            description_analysis,
            reviews_analysis,
            genre_emotions
        )
        
        return combined_analysis
    
    def _combine_emotional_signals(self, 
                                  description_analysis: Dict, 
                                  reviews_analysis: Dict, 
                                  genre_emotions: Dict) -> Dict:
        """
        Combine emotional signals from different sources.
        
        Args:
            description_analysis: Analysis of book description
            reviews_analysis: Analysis of book reviews
            genre_emotions: Emotions extracted from genres
            
        Returns:
            Combined emotional analysis
        """
        # Initialize combined analysis
        combined = {
            'primary_emotions': [],
            'emotional_arc': {
                'beginning': [],
                'middle': [],
                'end': []
            },
            'unexpected_emotions': [],
            'lasting_impact': '',
            'emotional_keywords': [],
            'overall_emotional_profile': ''
        }
        
        # Combine primary emotions
        desc_emotions = {e['emotion']: e['intensity'] for e in description_analysis.get('primary_emotions', [])}
        review_emotions = {e['emotion']: e['intensity'] for e in reviews_analysis.get('primary_emotions', [])}
        
        all_emotions = set(list(desc_emotions.keys()) + list(review_emotions.keys()) + list(genre_emotions.keys()))
        
        for emotion in all_emotions:
            # Calculate weighted average
            desc_weight = 0.4
            review_weight = 0.5
            genre_weight = 0.1
            
            desc_value = desc_emotions.get(emotion, 0)
            review_value = review_emotions.get(emotion, 0)
            genre_value = genre_emotions.get(emotion, 0) * 10  # Scale up to 0-10
            
            # If one source doesn't have this emotion, adjust weights
            total_weight = 0
            weighted_sum = 0
            
            if desc_value > 0:
                weighted_sum += desc_value * desc_weight
                total_weight += desc_weight
            
            if review_value > 0:
                weighted_sum += review_value * review_weight
                total_weight += review_weight
            
            if genre_value > 0:
                weighted_sum += genre_value * genre_weight
                total_weight += genre_weight
            
            if total_weight > 0:
                intensity = weighted_sum / total_weight
                combined['primary_emotions'].append({
                    'emotion': emotion,
                    'intensity': round(intensity, 1)
                })
        
        # Sort emotions by intensity (descending)
        combined['primary_emotions'].sort(key=lambda x: x['intensity'], reverse=True)
        
        # Combine emotional arc
        for stage in ['beginning', 'middle', 'end']:
            desc_arc = description_analysis.get('emotional_arc', {}).get(stage, [])
            review_arc = reviews_analysis.get('emotional_arc', {}).get(stage, [])
            
            # Prioritize review arc but include unique emotions from description
            combined['emotional_arc'][stage] = list(review_arc)
            for emotion in desc_arc:
                if emotion not in combined['emotional_arc'][stage]:
                    combined['emotional_arc'][stage].append(emotion)
        
        # Combine unexpected emotions
        desc_unexpected = description_analysis.get('unexpected_emotions', [])
        review_unexpected = reviews_analysis.get('unexpected_emotions', [])
        
        combined['unexpected_emotions'] = list(set(desc_unexpected + review_unexpected))
        
        # Combine lasting impact (prioritize reviews)
        if reviews_analysis.get('lasting_impact'):
            combined['lasting_impact'] = reviews_analysis['lasting_impact']
        else:
            combined['lasting_impact'] = description_analysis.get('lasting_impact', '')
        
        # Combine emotional keywords
        desc_keywords = description_analysis.get('emotional_keywords', [])
        review_keywords = reviews_analysis.get('emotional_keywords', [])
        
        combined['emotional_keywords'] = list(set(desc_keywords + review_keywords))
        
        # Generate overall emotional profile
        if reviews_analysis.get('overall_emotional_profile'):
            combined['overall_emotional_profile'] = reviews_analysis['overall_emotional_profile']
        else:
            combined['overall_emotional_profile'] = description_analysis.get('overall_emotional_profile', '')
        
        return combined
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis when actual analysis fails."""
        return {
            'primary_emotions': [
                {'emotion': 'neutral', 'intensity': 5.0}
            ],
            'emotional_arc': {
                'beginning': ['neutral'],
                'middle': ['neutral'],
                'end': ['neutral']
            },
            'unexpected_emotions': [],
            'lasting_impact': 'Unknown',
            'emotional_keywords': [],
            'overall_emotional_profile': 'Neutral emotional profile'
        }


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Analyze emotional content of books using Google Books API')
    parser.add_argument('--query', help='Search query for books')
    parser.add_argument('--isbn', help='ISBN of the book')
    parser.add_argument('--id', help='Google Books ID')
    parser.add_argument('--output', default='book_emotional_analysis.json', help='Output JSON file')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    
    args = parser.parse_args()
    
    if not args.query and not args.isbn and not args.id:
        parser.error("At least one of --query, --isbn, or --id must be provided")
    
    try:
        # Initialize clients
        google_books = GoogleBooksClient()
        analyzer = EmotionalAnalyzer(use_cache=not args.no_cache)
        
        # Get book data
        book = None
        if args.id:
            book = google_books.get_book_by_id(args.id)
        elif args.isbn:
            book = google_books.get_book_by_isbn(args.isbn)
        elif args.query:
            books = google_books.search_book(args.query)
            if books:
                book = books[0]
        
        if not book:
            logger.error("No book found")
            return
        
        # Get reviews
        book['reviews'] = google_books.get_book_reviews(book['id'])
        
        # Create emotional profile
        emotional_profile = analyzer.create_emotional_profile(book)
        
        # Add emotional profile to book data
        book['emotional_profile'] = emotional_profile
        
        # Save to file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(book, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved book emotional analysis to {args.output}")
        
        # Print summary
        print(f"\nBook: {book['title']} by {', '.join(book['authors'])}")
        print("\nTop Emotions:")
        for emotion in emotional_profile['primary_emotions'][:5]:
            print(f"- {emotion['emotion']}: {emotion['intensity']}/10")
        
        print("\nEmotional Arc:")
        for stage, emotions in emotional_profile['emotional_arc'].items():
            print(f"- {stage.capitalize()}: {', '.join(emotions[:3])}")
        
        print(f"\nOverall Profile: {emotional_profile['overall_emotional_profile']}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == '__main__':
    main() 