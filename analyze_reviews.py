#!/usr/bin/env python3
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import re
from wordcloud import WordCloud
import os

def load_reviews(json_file):
    """Load reviews from a JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading reviews: {e}")
        return None

def calculate_stats(reviews):
    """Calculate basic statistics from reviews."""
    if not reviews:
        return {}
    
    # Extract ratings and word counts
    ratings = [review.get('rating', 0) for review in reviews]
    word_counts = [review.get('word_count', 0) for review in reviews]
    likes = [review.get('likes', 0) for review in reviews]
    
    # Calculate sentiment stats if available
    sentiment_stats = {}
    if 'sentiment' in reviews[0]:
        polarities = [review['sentiment']['polarity'] for review in reviews if 'sentiment' in review]
        subjectivities = [review['sentiment']['subjectivity'] for review in reviews if 'sentiment' in review]
        
        sentiment_stats = {
            'avg_polarity': sum(polarities) / len(polarities) if polarities else 0,
            'avg_subjectivity': sum(subjectivities) / len(subjectivities) if subjectivities else 0,
            'positive_reviews': sum(1 for p in polarities if p > 0.1),
            'negative_reviews': sum(1 for p in polarities if p < -0.1),
            'neutral_reviews': sum(1 for p in polarities if -0.1 <= p <= 0.1)
        }
    
    return {
        'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
        'avg_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
        'avg_likes': sum(likes) / len(likes) if likes else 0,
        'total_reviews': len(reviews),
        'rating_distribution': Counter(ratings),
        'sentiment': sentiment_stats
    }

def generate_word_cloud(reviews, output_file='wordcloud.png', stopwords=None):
    """Generate a word cloud from review texts."""
    try:
        import nltk
        from nltk.corpus import stopwords as nltk_stopwords
        
        # Download stopwords if not already downloaded
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Combine all review texts
        all_text = ' '.join([review.get('text', '') for review in reviews])
        
        # Clean text
        all_text = re.sub(r'[^\w\s]', '', all_text.lower())
        
        # Get stopwords
        if stopwords is None:
            stopwords = set(nltk_stopwords.words('english'))
            # Add custom stopwords
            custom_stopwords = {'book', 'read', 'reading', 'story', 'character', 'characters', 'one', 'like', 'just', 'really', 'much', 'even', 'also', 'get', 'well', 'way', 'make', 'made', 'time', 'good', 'great', 'lot', 'thing', 'things', 'going', 'got', 'go', 'goes', 'went', 'say', 'said', 'says', 'see', 'saw', 'seen', 'look', 'looked', 'looking', 'looks', 'come', 'came', 'coming', 'comes', 'know', 'knew', 'known', 'knows', 'think', 'thought', 'thinking', 'thinks', 'want', 'wanted', 'wanting', 'wants', 'feel', 'felt', 'feeling', 'feels', 'find', 'found', 'finding', 'finds', 'give', 'gave', 'giving', 'gives', 'take', 'took', 'taking', 'takes', 'put', 'putting', 'puts', 'use', 'used', 'using', 'uses', 'work', 'worked', 'working', 'works', 'try', 'tried', 'trying', 'tries', 'need', 'needed', 'needing', 'needs', 'start', 'started', 'starting', 'starts', 'end', 'ended', 'ending', 'ends', 'seem', 'seemed', 'seeming', 'seems', 'show', 'showed', 'showing', 'shows', 'ask', 'asked', 'asking', 'asks', 'turn', 'turned', 'turning', 'turns', 'call', 'called', 'calling', 'calls', 'help', 'helped', 'helping', 'helps', 'play', 'played', 'playing', 'plays', 'move', 'moved', 'moving', 'moves', 'live', 'lived', 'living', 'lives', 'believe', 'believed', 'believing', 'believes', 'hold', 'held', 'holding', 'holds', 'bring', 'brought', 'bringing', 'brings', 'happen', 'happened', 'happening', 'happens', 'write', 'wrote', 'writing', 'writes', 'sit', 'sat', 'sitting', 'sits', 'stand', 'stood', 'standing', 'stands', 'hear', 'heard', 'hearing', 'hears', 'let', 'letting', 'lets', 'mean', 'meant', 'meaning', 'means', 'keep', 'kept', 'keeping', 'keeps', 'allow', 'allowed', 'allowing', 'allows', 'add', 'added', 'adding', 'adds', 'spend', 'spent', 'spending', 'spends', 'grow', 'grew', 'growing', 'grows', 'open', 'opened', 'opening', 'opens', 'walk', 'walked', 'walking', 'walks', 'win', 'won', 'winning', 'wins', 'offer', 'offered', 'offering', 'offers', 'remember', 'remembered', 'remembering', 'remembers', 'love', 'loved', 'loving', 'loves', 'consider', 'considered', 'considering', 'considers', 'appear', 'appeared', 'appearing', 'appears', 'buy', 'bought', 'buying', 'buys', 'wait', 'waited', 'waiting', 'waits', 'serve', 'served', 'serving', 'serves', 'die', 'died', 'dying', 'dies', 'send', 'sent', 'sending', 'sends', 'expect', 'expected', 'expecting', 'expects', 'build', 'built', 'building', 'builds', 'stay', 'stayed', 'staying', 'stays', 'fall', 'fell', 'falling', 'falls', 'cut', 'cutting', 'cuts', 'reach', 'reached', 'reaching', 'reaches', 'kill', 'killed', 'killing', 'kills', 'remain', 'remained', 'remaining', 'remains'}
            stopwords.update(custom_stopwords)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            stopwords=stopwords,
            max_words=100,
            contour_width=3,
            contour_color='steelblue'
        ).generate(all_text)
        
        # Save the image
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        print(f"Word cloud saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error generating word cloud: {e}")
        return False

def plot_rating_distribution(stats, output_file='rating_distribution.png'):
    """Plot the distribution of ratings."""
    try:
        ratings = stats['rating_distribution']
        
        # Create a bar chart
        plt.figure(figsize=(10, 6))
        
        # Get all possible ratings (1-5)
        all_ratings = list(range(1, 6))
        counts = [ratings.get(rating, 0) for rating in all_ratings]
        
        # Plot
        bars = plt.bar(all_ratings, counts, color='skyblue')
        
        # Add count labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.xlabel('Rating')
        plt.ylabel('Number of Reviews')
        plt.title('Distribution of Ratings')
        plt.xticks(all_ratings)
        plt.ylim(0, max(counts) * 1.2)  # Add some space for the labels
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        print(f"Rating distribution plot saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error plotting rating distribution: {e}")
        return False

def plot_sentiment_analysis(stats, output_file='sentiment_analysis.png'):
    """Plot sentiment analysis results."""
    try:
        if not stats.get('sentiment'):
            print("No sentiment data available.")
            return False
        
        sentiment = stats['sentiment']
        
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: Sentiment distribution (positive, negative, neutral)
        sentiment_counts = [
            sentiment.get('positive_reviews', 0),
            sentiment.get('neutral_reviews', 0),
            sentiment.get('negative_reviews', 0)
        ]
        sentiment_labels = ['Positive', 'Neutral', 'Negative']
        
        # Plot pie chart
        ax1.pie(sentiment_counts, labels=sentiment_labels, autopct='%1.1f%%',
                colors=['#4CAF50', '#FFC107', '#F44336'], startangle=90)
        ax1.set_title('Sentiment Distribution')
        
        # Plot 2: Average polarity and subjectivity
        metrics = ['Polarity', 'Subjectivity']
        values = [sentiment.get('avg_polarity', 0), sentiment.get('avg_subjectivity', 0)]
        
        # Plot horizontal bar chart
        bars = ax2.barh(metrics, values, color=['#2196F3', '#9C27B0'])
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width >= 0 else 0
            ax2.text(label_x_pos + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.2f}',
                    va='center')
        
        ax2.set_xlim(-1, 1)
        ax2.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
        ax2.set_title('Average Sentiment Metrics')
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        print(f"Sentiment analysis plot saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error plotting sentiment analysis: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Analyze Goodreads reviews')
    parser.add_argument('--input', default='goodreads_reviews.json', help='Input JSON file with reviews')
    parser.add_argument('--output-dir', default='analysis_results', help='Directory to save analysis results')
    
    args = parser.parse_args()
    
    # Load reviews
    data = load_reviews(args.input)
    if not data:
        print(f"Failed to load reviews from {args.input}")
        return
    
    reviews = data.get('reviews', [])
    if not reviews:
        print("No reviews found in the data")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Calculate statistics
    stats = calculate_stats(reviews)
    
    # Print basic statistics
    print("\n=== Review Statistics ===")
    print(f"Total reviews: {stats['total_reviews']}")
    print(f"Average rating: {stats['avg_rating']:.2f}/5")
    print(f"Average word count: {stats['avg_word_count']:.0f} words")
    print(f"Average likes: {stats['avg_likes']:.0f} likes")
    
    if stats.get('sentiment'):
        print("\n=== Sentiment Analysis ===")
        print(f"Average polarity: {stats['sentiment']['avg_polarity']:.2f} (-1 to 1, negative to positive)")
        print(f"Average subjectivity: {stats['sentiment']['avg_subjectivity']:.2f} (0 to 1, objective to subjective)")
        print(f"Positive reviews: {stats['sentiment']['positive_reviews']} ({stats['sentiment']['positive_reviews']/stats['total_reviews']*100:.1f}%)")
        print(f"Neutral reviews: {stats['sentiment']['neutral_reviews']} ({stats['sentiment']['neutral_reviews']/stats['total_reviews']*100:.1f}%)")
        print(f"Negative reviews: {stats['sentiment']['negative_reviews']} ({stats['sentiment']['negative_reviews']/stats['total_reviews']*100:.1f}%)")
    
    # Generate visualizations
    wordcloud_path = os.path.join(args.output_dir, 'wordcloud.png')
    generate_word_cloud(reviews, wordcloud_path)
    
    rating_dist_path = os.path.join(args.output_dir, 'rating_distribution.png')
    plot_rating_distribution(stats, rating_dist_path)
    
    if stats.get('sentiment'):
        sentiment_path = os.path.join(args.output_dir, 'sentiment_analysis.png')
        plot_sentiment_analysis(stats, sentiment_path)
    
    # Save statistics to JSON
    stats_path = os.path.join(args.output_dir, 'review_stats.json')
    try:
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        print(f"\nStatistics saved to {stats_path}")
    except Exception as e:
        print(f"Error saving statistics: {e}")

if __name__ == '__main__':
    main() 