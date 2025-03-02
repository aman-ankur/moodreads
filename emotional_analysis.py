#!/usr/bin/env python3
import json
import os
import argparse
from datetime import datetime
import anthropic
from dotenv import load_dotenv
import time
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Get API key from environment variable
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def load_reviews(json_file):
    """Load reviews from a JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading reviews: {e}")
        return None

def save_enhanced_reviews(data, output_file):
    """Save enhanced reviews to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved enhanced reviews to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving enhanced reviews: {e}")
        return False

def analyze_review_emotions(review_text, book_title=None, genre=None):
    """
    Analyze the emotional content of a review using Claude API.
    
    Args:
        review_text: The text of the review
        book_title: The title of the book (optional)
        genre: The genre of the book (optional)
        
    Returns:
        dict: Emotional analysis results
    """
    if not CLAUDE_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    # Construct the prompt
    context = ""
    if book_title:
        context += f"Book Title: {book_title}\n"
    if genre:
        context += f"Book Genre: {genre}\n"
    
    prompt = f"""
{context}
Below is a review of a book. Please analyze the emotional content of this review and extract the following information:

1. Primary emotions experienced by the reader (joy, sadness, tension, comfort, etc.)
2. Emotional intensity scores (on a scale of 1-10) for each primary emotion
3. Emotional progression/arc described in the review (how the reader's emotions changed throughout the book)
4. Any unexpected emotional responses mentioned
5. Lasting emotional impact described by the reader
6. Emotional keywords and phrases from the review

Review:
{review_text}

Please provide your analysis in the following JSON format:
{{
  "primary_emotions": [
    {{"emotion": "emotion_name", "intensity": intensity_score}},
    ...
  ],
  "emotional_arc": {{
    "beginning": ["emotion1", "emotion2", ...],
    "middle": ["emotion1", "emotion2", ...],
    "end": ["emotion1", "emotion2", ...]
  }},
  "unexpected_emotions": ["emotion1", "emotion2", ...],
  "lasting_impact": "description of lasting emotional impact",
  "emotional_keywords": ["keyword1", "keyword2", ...],
  "overall_emotional_profile": "brief summary of the overall emotional profile"
}}
"""

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.2,
            system="You are an expert literary analyst specializing in emotional analysis of book reviews. Your task is to extract nuanced emotional signals from reviews to create comprehensive emotional profiles for books.",
            messages=[
                {"role": "user", "content": prompt}
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
            return analysis
        except json.JSONDecodeError:
            print("Failed to parse JSON from Claude's response. Using raw response.")
            return {"error": "JSON parsing failed", "raw_response": response_text}
            
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return {"error": str(e)}

def analyze_book_emotions_from_reviews(reviews, book_title=None, genre=None):
    """
    Analyze the emotional content of a book based on multiple reviews.
    
    Args:
        reviews: List of review dictionaries
        book_title: The title of the book (optional)
        genre: The genre of the book (optional)
        
    Returns:
        dict: Aggregated emotional analysis
    """
    # Combine all review texts
    all_review_text = "\n\n".join([f"Review {i+1}:\n{review.get('text', '')}" for i, review in enumerate(reviews)])
    
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    # Construct the prompt
    context = ""
    if book_title:
        context += f"Book Title: {book_title}\n"
    if genre:
        context += f"Book Genre: {genre}\n"
    
    prompt = f"""
{context}
Below are multiple reviews of a book. Please analyze these reviews collectively to create a comprehensive emotional profile of the book. Extract the following information:

1. Primary emotions evoked by the book (joy, sadness, tension, comfort, etc.)
2. Emotional intensity scores (on a scale of 1-10) for each primary emotion
3. Emotional progression/arc throughout the book (beginning, middle, end)
4. Unexpected emotional responses mentioned by readers
5. Lasting emotional impact described by readers
6. Emotional keywords and phrases from the reviews

Reviews:
{all_review_text}

Please provide your analysis in the following JSON format:
{{
  "primary_emotions": [
    {{"emotion": "emotion_name", "intensity": intensity_score}},
    ...
  ],
  "emotional_arc": {{
    "beginning": ["emotion1", "emotion2", ...],
    "middle": ["emotion1", "emotion2", ...],
    "end": ["emotion1", "emotion2", ...]
  }},
  "unexpected_emotions": ["emotion1", "emotion2", ...],
  "lasting_impact": "description of lasting emotional impact",
  "emotional_keywords": ["keyword1", "keyword2", ...],
  "overall_emotional_profile": "brief summary of the overall emotional profile"
}}
"""

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0.2,
            system="You are an expert literary analyst specializing in emotional analysis of book reviews. Your task is to extract nuanced emotional signals from reviews to create comprehensive emotional profiles for books.",
            messages=[
                {"role": "user", "content": prompt}
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
            return analysis
        except json.JSONDecodeError:
            print("Failed to parse JSON from Claude's response. Using raw response.")
            return {"error": "JSON parsing failed", "raw_response": response_text}
            
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return {"error": str(e)}

def enhance_reviews_with_emotions(reviews_data, book_title=None, genre=None, analyze_individual=False, analyze_collective=True):
    """
    Enhance reviews with emotional analysis.
    
    Args:
        reviews_data: Dictionary containing reviews data
        book_title: The title of the book (optional)
        genre: The genre of the book (optional)
        analyze_individual: Whether to analyze each review individually
        analyze_collective: Whether to analyze all reviews collectively
        
    Returns:
        dict: Enhanced reviews data with emotional analysis
    """
    enhanced_data = reviews_data.copy()
    reviews = enhanced_data.get('reviews', [])
    
    # Add metadata if not present
    if 'metadata' not in enhanced_data:
        enhanced_data['metadata'] = {
            'extraction_date': datetime.now().isoformat(),
            'review_count': len(reviews)
        }
    
    # Add emotional analysis timestamp
    enhanced_data['metadata']['emotional_analysis_date'] = datetime.now().isoformat()
    
    # Analyze individual reviews if requested
    if analyze_individual:
        print(f"Analyzing emotions in {len(reviews)} individual reviews...")
        for i, review in enumerate(tqdm(reviews)):
            # Skip reviews that already have emotional analysis
            if 'emotional_analysis' in review:
                continue
                
            # Analyze emotions in the review
            emotional_analysis = analyze_review_emotions(
                review.get('text', ''),
                book_title=book_title,
                genre=genre
            )
            
            # Add emotional analysis to the review
            review['emotional_analysis'] = emotional_analysis
            
            # Add a small delay to avoid rate limiting
            if i < len(reviews) - 1:
                time.sleep(1)
    
    # Analyze all reviews collectively if requested
    if analyze_collective and reviews:
        print("Analyzing collective emotions from all reviews...")
        book_emotional_profile = analyze_book_emotions_from_reviews(
            reviews,
            book_title=book_title,
            genre=genre
        )
        
        # Add book emotional profile to the data
        enhanced_data['book_emotional_profile'] = book_emotional_profile
    
    return enhanced_data

def main():
    parser = argparse.ArgumentParser(description='Enhance Goodreads reviews with emotional analysis')
    parser.add_argument('--input', default='goodreads_reviews.json', help='Input JSON file with reviews')
    parser.add_argument('--output', default='enhanced_reviews.json', help='Output JSON file for enhanced reviews')
    parser.add_argument('--title', help='Book title (optional)')
    parser.add_argument('--genre', help='Book genre (optional)')
    parser.add_argument('--individual', action='store_true', help='Analyze each review individually')
    parser.add_argument('--collective', action='store_true', default=True, help='Analyze all reviews collectively')
    parser.add_argument('--no-collective', action='store_false', dest='collective', help='Skip collective analysis')
    
    args = parser.parse_args()
    
    # Check if Claude API key is set
    if not CLAUDE_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set the environment variable or create a .env file with ANTHROPIC_API_KEY=your_api_key")
        return
    
    # Load reviews
    data = load_reviews(args.input)
    if not data:
        print(f"Failed to load reviews from {args.input}")
        return
    
    reviews = data.get('reviews', [])
    if not reviews:
        print("No reviews found in the data")
        return
    
    # Enhance reviews with emotional analysis
    enhanced_data = enhance_reviews_with_emotions(
        data,
        book_title=args.title,
        genre=args.genre,
        analyze_individual=args.individual,
        analyze_collective=args.collective
    )
    
    # Save enhanced reviews
    save_enhanced_reviews(enhanced_data, args.output)
    
    # Print summary
    print("\n=== Emotional Analysis Summary ===")
    if 'book_emotional_profile' in enhanced_data:
        profile = enhanced_data['book_emotional_profile']
        print("Book Emotional Profile:")
        
        if 'primary_emotions' in profile:
            print("\nPrimary Emotions:")
            for emotion in profile['primary_emotions']:
                print(f"  - {emotion['emotion']}: {emotion['intensity']}/10")
        
        if 'emotional_arc' in profile:
            print("\nEmotional Arc:")
            arc = profile['emotional_arc']
            print(f"  Beginning: {', '.join(arc.get('beginning', []))}")
            print(f"  Middle: {', '.join(arc.get('middle', []))}")
            print(f"  End: {', '.join(arc.get('end', []))}")
        
        if 'emotional_keywords' in profile:
            print("\nEmotional Keywords:")
            print(f"  {', '.join(profile['emotional_keywords'][:10])}...")
        
        if 'overall_emotional_profile' in profile:
            print("\nOverall Emotional Profile:")
            print(f"  {profile['overall_emotional_profile']}")
    
    individual_count = sum(1 for review in enhanced_data.get('reviews', []) if 'emotional_analysis' in review)
    print(f"\nIndividual reviews analyzed: {individual_count}/{len(enhanced_data.get('reviews', []))}")
    
    print(f"\nEnhanced reviews saved to {args.output}")

if __name__ == "__main__":
    main() 