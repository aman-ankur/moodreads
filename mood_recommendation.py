#!/usr/bin/env python3
import json
import os
import argparse
from datetime import datetime
import anthropic
from dotenv import load_dotenv
import time
from tqdm import tqdm
import glob
import re
from collections import defaultdict

# Load environment variables
load_dotenv()

# Get API key from environment variable
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def load_enhanced_reviews(json_file):
    """Load enhanced reviews from a JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading enhanced reviews: {e}")
        return None

def load_all_book_profiles(directory):
    """
    Load all book emotional profiles from a directory.
    
    Args:
        directory: Directory containing enhanced review JSON files
        
    Returns:
        dict: Dictionary of book profiles keyed by book title
    """
    book_profiles = {}
    
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    for json_file in json_files:
        try:
            # Extract book title from filename
            filename = os.path.basename(json_file)
            book_title = re.sub(r'_enhanced\.json$', '', filename).replace('_', ' ').title()
            
            # Load enhanced reviews
            data = load_enhanced_reviews(json_file)
            
            if data and 'book_emotional_profile' in data:
                # Add book title to the profile
                profile = data['book_emotional_profile']
                profile['book_title'] = book_title
                
                # Add to book profiles
                book_profiles[book_title] = profile
                print(f"Loaded emotional profile for '{book_title}'")
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return book_profiles

def analyze_user_mood_query(query):
    """
    Analyze a user's mood query using Claude API.
    
    Args:
        query: User's mood query
        
    Returns:
        dict: Emotional preferences extracted from the query
    """
    if not CLAUDE_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    prompt = f"""
Analyze the following user query about their mood and what kind of book they want to read. Extract the following information:

1. Current emotional state of the user
2. Desired emotional experience they want from a book
3. Any specific emotional journey or arc they're looking for
4. Emotional intensity preferences (high, medium, low)
5. Relevant emotional keywords from their query

User Query:
{query}

Please provide your analysis in the following JSON format:
{{
  "current_emotional_state": ["emotion1", "emotion2", ...],
  "desired_emotional_experience": ["emotion1", "emotion2", ...],
  "emotional_journey": {{
    "beginning": ["emotion1", "emotion2", ...],
    "middle": ["emotion1", "emotion2", ...],
    "end": ["emotion1", "emotion2", ...]
  }},
  "intensity_preference": "high/medium/low",
  "emotional_keywords": ["keyword1", "keyword2", ...],
  "summary": "brief summary of the user's emotional preferences"
}}
"""

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.2,
            system="You are an expert in understanding emotional preferences from user queries. Your task is to extract nuanced emotional signals from a user's request to help match them with appropriate book recommendations.",
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

def calculate_emotion_similarity(user_emotions, book_emotions):
    """
    Calculate similarity between user emotional preferences and book emotional profile.
    
    Args:
        user_emotions: List of emotions from user query
        book_emotions: List of emotions from book profile
        
    Returns:
        float: Similarity score (0-1)
    """
    if not user_emotions or not book_emotions:
        return 0
    
    # Convert to lowercase for comparison
    user_emotions_lower = [e.lower() for e in user_emotions]
    book_emotions_lower = [e.lower() for e in book_emotions]
    
    # Count matching emotions
    matches = sum(1 for e in user_emotions_lower if e in book_emotions_lower)
    
    # Calculate similarity score
    similarity = matches / max(len(user_emotions_lower), 1)
    
    return similarity

def calculate_keyword_similarity(user_keywords, book_keywords):
    """
    Calculate similarity between user keywords and book keywords.
    
    Args:
        user_keywords: List of keywords from user query
        book_keywords: List of keywords from book profile
        
    Returns:
        float: Similarity score (0-1)
    """
    if not user_keywords or not book_keywords:
        return 0
    
    # Convert to lowercase for comparison
    user_keywords_lower = [k.lower() for k in user_keywords]
    book_keywords_lower = [k.lower() for k in book_keywords]
    
    # Count matching keywords
    matches = sum(1 for k in user_keywords_lower if k in book_keywords_lower)
    
    # Calculate similarity score
    similarity = matches / max(len(user_keywords_lower), 1)
    
    return similarity

def calculate_arc_similarity(user_arc, book_arc):
    """
    Calculate similarity between user emotional arc preferences and book emotional arc.
    
    Args:
        user_arc: Dictionary of user arc preferences
        book_arc: Dictionary of book emotional arc
        
    Returns:
        float: Similarity score (0-1)
    """
    if not user_arc or not book_arc:
        return 0
    
    similarities = []
    
    # Compare each stage of the arc
    for stage in ['beginning', 'middle', 'end']:
        user_emotions = user_arc.get(stage, [])
        book_emotions = book_arc.get(stage, [])
        
        if user_emotions and book_emotions:
            stage_similarity = calculate_emotion_similarity(user_emotions, book_emotions)
            similarities.append(stage_similarity)
    
    # Calculate average similarity across all stages
    if similarities:
        return sum(similarities) / len(similarities)
    else:
        return 0

def match_books_to_mood(user_preferences, book_profiles, top_n=5):
    """
    Match books to user mood preferences.
    
    Args:
        user_preferences: Dictionary of user emotional preferences
        book_profiles: Dictionary of book emotional profiles
        top_n: Number of top matches to return
        
    Returns:
        list: List of top matching books with scores and explanations
    """
    matches = []
    
    for book_title, profile in book_profiles.items():
        # Skip books with incomplete profiles
        if not profile.get('primary_emotions') or not profile.get('emotional_keywords'):
            continue
        
        # Extract book emotions and keywords
        book_emotions = [e['emotion'] for e in profile.get('primary_emotions', [])]
        book_keywords = profile.get('emotional_keywords', [])
        book_arc = profile.get('emotional_arc', {})
        
        # Extract user preferences
        user_desired_emotions = user_preferences.get('desired_emotional_experience', [])
        user_keywords = user_preferences.get('emotional_keywords', [])
        user_arc = user_preferences.get('emotional_journey', {})
        
        # Calculate similarity scores
        emotion_similarity = calculate_emotion_similarity(user_desired_emotions, book_emotions)
        keyword_similarity = calculate_keyword_similarity(user_keywords, book_keywords)
        arc_similarity = calculate_arc_similarity(user_arc, book_arc)
        
        # Calculate weighted composite score
        # Weights: emotions (0.5), keywords (0.3), arc (0.2)
        composite_score = (emotion_similarity * 0.5) + (keyword_similarity * 0.3) + (arc_similarity * 0.2)
        
        # Generate explanation
        explanation = generate_match_explanation(
            book_title,
            user_preferences,
            profile,
            emotion_similarity,
            keyword_similarity,
            arc_similarity
        )
        
        # Add to matches
        matches.append({
            'book_title': book_title,
            'score': composite_score,
            'explanation': explanation,
            'emotion_similarity': emotion_similarity,
            'keyword_similarity': keyword_similarity,
            'arc_similarity': arc_similarity
        })
    
    # Sort by score (descending)
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top N matches
    return matches[:top_n]

def generate_match_explanation(book_title, user_preferences, book_profile, emotion_similarity, keyword_similarity, arc_similarity):
    """
    Generate an explanation for why a book was recommended.
    
    Args:
        book_title: Title of the book
        user_preferences: User emotional preferences
        book_profile: Book emotional profile
        emotion_similarity: Emotion similarity score
        keyword_similarity: Keyword similarity score
        arc_similarity: Arc similarity score
        
    Returns:
        str: Explanation for the recommendation
    """
    explanation = f"'{book_title}' matches your mood because:\n"
    
    # Add emotion match explanation
    if emotion_similarity > 0:
        user_emotions = user_preferences.get('desired_emotional_experience', [])
        book_emotions = [e['emotion'] for e in book_profile.get('primary_emotions', [])]
        matching_emotions = [e for e in user_emotions if e.lower() in [be.lower() for be in book_emotions]]
        
        if matching_emotions:
            explanation += f"- It evokes {', '.join(matching_emotions)} as you desired\n"
    
    # Add keyword match explanation
    if keyword_similarity > 0:
        user_keywords = user_preferences.get('emotional_keywords', [])
        book_keywords = book_profile.get('emotional_keywords', [])
        matching_keywords = [k for k in user_keywords if k.lower() in [bk.lower() for bk in book_keywords]]
        
        if matching_keywords:
            explanation += f"- It contains emotional elements like {', '.join(matching_keywords)}\n"
    
    # Add arc match explanation
    if arc_similarity > 0:
        user_arc = user_preferences.get('emotional_journey', {})
        book_arc = book_profile.get('emotional_arc', {})
        
        arc_matches = []
        for stage in ['beginning', 'middle', 'end']:
            user_emotions = user_arc.get(stage, [])
            book_emotions = book_arc.get(stage, [])
            matching_emotions = [e for e in user_emotions if e.lower() in [be.lower() for be in book_emotions]]
            
            if matching_emotions:
                arc_matches.append(f"the {stage} evokes {', '.join(matching_emotions)}")
        
        if arc_matches:
            explanation += f"- The emotional journey matches your preferences: {'; '.join(arc_matches)}\n"
    
    # Add overall emotional profile
    if 'overall_emotional_profile' in book_profile:
        explanation += f"- Overall emotional profile: {book_profile['overall_emotional_profile']}\n"
    
    return explanation

def main():
    parser = argparse.ArgumentParser(description='Match books to user mood query')
    parser.add_argument('--query', required=True, help='User mood query')
    parser.add_argument('--books-dir', default='enhanced_books', help='Directory containing enhanced book reviews')
    parser.add_argument('--top-n', type=int, default=5, help='Number of top matches to return')
    parser.add_argument('--output', help='Output JSON file for recommendations (optional)')
    
    args = parser.parse_args()
    
    # Check if Claude API key is set
    if not CLAUDE_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set the environment variable or create a .env file with ANTHROPIC_API_KEY=your_api_key")
        return
    
    try:
        # Create books directory if it doesn't exist
        if not os.path.exists(args.books_dir):
            os.makedirs(args.books_dir)
            print(f"Created directory: {args.books_dir}")
            print("Please add enhanced book review JSON files to this directory")
            return
        
        # Load all book profiles
        print(f"Loading book profiles from {args.books_dir}...")
        book_profiles = load_all_book_profiles(args.books_dir)
        
        if not book_profiles:
            print("No book profiles found. Please add enhanced book review JSON files to the books directory.")
            return
        
        print(f"Loaded {len(book_profiles)} book profiles")
        
        # Analyze user mood query
        print(f"Analyzing user mood query: '{args.query}'")
        user_preferences = analyze_user_mood_query(args.query)
        
        if 'error' in user_preferences:
            print(f"Error analyzing user query: {user_preferences['error']}")
            return
        
        print("\n=== User Mood Analysis ===")
        print(f"Current emotional state: {', '.join(user_preferences.get('current_emotional_state', []))}")
        print(f"Desired emotional experience: {', '.join(user_preferences.get('desired_emotional_experience', []))}")
        print(f"Intensity preference: {user_preferences.get('intensity_preference', 'unknown')}")
        print(f"Emotional keywords: {', '.join(user_preferences.get('emotional_keywords', []))}")
        
        if 'emotional_journey' in user_preferences:
            journey = user_preferences['emotional_journey']
            print("\nDesired emotional journey:")
            print(f"  Beginning: {', '.join(journey.get('beginning', []))}")
            print(f"  Middle: {', '.join(journey.get('middle', []))}")
            print(f"  End: {', '.join(journey.get('end', []))}")
        
        print(f"\nSummary: {user_preferences.get('summary', '')}")
        
        # Match books to mood
        print("\nMatching books to mood...")
        matches = match_books_to_mood(user_preferences, book_profiles, args.top_n)
        
        # Print recommendations
        print("\n=== Book Recommendations ===")
        for i, match in enumerate(matches):
            print(f"\n{i+1}. {match['book_title']} (Score: {match['score']:.2f})")
            print(match['explanation'])
        
        # Save recommendations to JSON if requested
        if args.output:
            recommendations = {
                'metadata': {
                    'query': args.query,
                    'timestamp': datetime.now().isoformat(),
                    'user_preferences': user_preferences
                },
                'recommendations': matches
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2, ensure_ascii=False)
            
            print(f"\nRecommendations saved to {args.output}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 