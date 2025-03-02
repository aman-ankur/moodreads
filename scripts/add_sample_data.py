#!/usr/bin/env python3
"""
Script to add sample books with reviews and emotional profiles for testing.
This script adds sample data to the database to test the enhanced recommendation system.
"""

import logging
import sys
import json
from datetime import datetime

from moodreads.database.mongodb import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('add_sample_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Sample books with reviews and emotional profiles
SAMPLE_BOOKS = [
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "url": "https://www.goodreads.com/book/show/865.The_Alchemist",
        "description": "Paulo Coelho's enchanting novel has inspired a devoted following around the world. This story, dazzling in its powerful simplicity and soul-stirring wisdom, is about an Andalusian shepherd boy named Santiago who travels from his homeland in Spain to the Egyptian desert in search of a treasure buried near the Pyramids. Along the way he meets a Gypsy woman, a man who calls himself king, and an alchemist, all of whom point Santiago in the direction of his quest. No one knows what the treasure is, or if Santiago will be able to surmount the obstacles in his path. But what starts out as a journey to find worldly goods turns into a discovery of the treasure found within. Lush, evocative, and deeply humane, the story of Santiago is an eternal testament to the transforming power of our dreams and the importance of listening to our hearts.",
        "genres": ["Fiction", "Philosophy", "Spirituality", "Self Help"],
        "rating": 4.2,
        "reviews": [
            "This book changed my life. It's a beautiful story about following your dreams.",
            "I found this book to be incredibly inspiring. The journey of self-discovery resonated with me.",
            "A simple yet profound tale that reminds us to listen to our hearts and follow our dreams.",
            "The spiritual symbolism throughout the book is beautiful and thought-provoking.",
            "I loved how this book encouraged me to pursue my own personal legend."
        ],
        "reviews_data": {
            "book_id": "865",
            "book_title": "The Alchemist",
            "reviews": [
                {
                    "text": "This book changed my life. It's a beautiful story about following your dreams.",
                    "rating": 5,
                    "sentiment": 0.9
                },
                {
                    "text": "I found this book to be incredibly inspiring. The journey of self-discovery resonated with me.",
                    "rating": 5,
                    "sentiment": 0.85
                },
                {
                    "text": "A simple yet profound tale that reminds us to listen to our hearts and follow our dreams.",
                    "rating": 4,
                    "sentiment": 0.8
                },
                {
                    "text": "The spiritual symbolism throughout the book is beautiful and thought-provoking.",
                    "rating": 4,
                    "sentiment": 0.75
                },
                {
                    "text": "I loved how this book encouraged me to pursue my own personal legend.",
                    "rating": 5,
                    "sentiment": 0.9
                }
            ],
            "metadata": {
                "total_reviews": 5,
                "average_rating": 4.6,
                "average_sentiment": 0.84
            }
        },
        "emotional_profile": {
            "inspiration": 0.9,
            "hope": 0.85,
            "wonder": 0.8,
            "joy": 0.7,
            "curiosity": 0.75,
            "reflection": 0.85,
            "satisfaction": 0.8
        },
        "emotional_arc": {
            "beginning": {
                "curiosity": 0.8,
                "hope": 0.7
            },
            "middle": {
                "tension": 0.6,
                "wonder": 0.8,
                "reflection": 0.7
            },
            "end": {
                "satisfaction": 0.9,
                "joy": 0.8,
                "inspiration": 0.95
            }
        },
        "emotional_keywords": [
            "inspiring",
            "hopeful",
            "spiritual",
            "transformative",
            "meaningful",
            "enlightening"
        ],
        "emotional_intensity": 0.75,
        "enhanced_emotional_profile": {
            "emotional_profile": {
                "inspiration": 0.9,
                "hope": 0.85,
                "wonder": 0.8,
                "joy": 0.7,
                "curiosity": 0.75,
                "reflection": 0.85,
                "satisfaction": 0.8,
                "peace": 0.7,
                "enlightenment": 0.8,
                "determination": 0.75
            },
            "emotional_arc": {
                "beginning": {
                    "curiosity": 0.8,
                    "hope": 0.7,
                    "uncertainty": 0.6
                },
                "middle": {
                    "tension": 0.6,
                    "wonder": 0.8,
                    "reflection": 0.7,
                    "determination": 0.7
                },
                "end": {
                    "satisfaction": 0.9,
                    "joy": 0.8,
                    "inspiration": 0.95,
                    "peace": 0.85,
                    "enlightenment": 0.9
                }
            },
            "emotional_keywords": [
                "inspiring",
                "hopeful",
                "spiritual",
                "transformative",
                "meaningful",
                "enlightening",
                "uplifting",
                "motivational",
                "introspective"
            ],
            "unexpected_emotions": [
                "melancholy",
                "longing",
                "nostalgia"
            ],
            "lasting_impact": "leaves readers with a renewed sense of purpose and motivation to pursue their dreams",
            "overall_emotional_profile": "offers a journey from uncertainty to enlightenment, with strong themes of hope and inspiration throughout",
            "emotional_intensity": 0.75
        }
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "url": "https://www.goodreads.com/book/show/5470.1984",
        "description": "Among the seminal texts of the 20th century, Nineteen Eighty-Four is a rare work that grows more haunting as its futuristic purgatory becomes more real. Published in 1949, the book offers political satirist George Orwell's nightmarish vision of a totalitarian, bureaucratic world and one poor stiff's attempt to find individuality. The brilliance of the novel is Orwell's prescience of modern life—the ubiquity of television, the distortion of the language—and his ability to construct such a thorough version of hell. Required reading for students since it was published, it ranks among the most terrifying novels ever written.",
        "genres": ["Fiction", "Classics", "Dystopia", "Science Fiction"],
        "rating": 4.3,
        "reviews": [
            "A chilling and prophetic novel that feels increasingly relevant in today's world.",
            "Orwell's masterpiece is a disturbing yet essential read about the dangers of totalitarianism.",
            "The world-building is incredible, creating a truly terrifying dystopian society.",
            "This book left me feeling unsettled and thoughtful about the nature of truth and freedom.",
            "A powerful and haunting story that stays with you long after you finish reading."
        ],
        "reviews_data": {
            "book_id": "5470",
            "book_title": "1984",
            "reviews": [
                {
                    "text": "A chilling and prophetic novel that feels increasingly relevant in today's world.",
                    "rating": 5,
                    "sentiment": 0.3
                },
                {
                    "text": "Orwell's masterpiece is a disturbing yet essential read about the dangers of totalitarianism.",
                    "rating": 5,
                    "sentiment": 0.2
                },
                {
                    "text": "The world-building is incredible, creating a truly terrifying dystopian society.",
                    "rating": 4,
                    "sentiment": 0.25
                },
                {
                    "text": "This book left me feeling unsettled and thoughtful about the nature of truth and freedom.",
                    "rating": 4,
                    "sentiment": 0.3
                },
                {
                    "text": "A powerful and haunting story that stays with you long after you finish reading.",
                    "rating": 5,
                    "sentiment": 0.4
                }
            ],
            "metadata": {
                "total_reviews": 5,
                "average_rating": 4.6,
                "average_sentiment": 0.29
            }
        },
        "emotional_profile": {
            "fear": 0.85,
            "tension": 0.9,
            "dread": 0.8,
            "sadness": 0.7,
            "anger": 0.65,
            "reflection": 0.8,
            "curiosity": 0.6
        },
        "emotional_arc": {
            "beginning": {
                "curiosity": 0.7,
                "tension": 0.6,
                "unease": 0.7
            },
            "middle": {
                "fear": 0.8,
                "tension": 0.9,
                "hope": 0.4
            },
            "end": {
                "dread": 0.9,
                "despair": 0.8,
                "reflection": 0.85
            }
        },
        "emotional_keywords": [
            "disturbing",
            "chilling",
            "terrifying",
            "haunting",
            "unsettling",
            "thought-provoking"
        ],
        "emotional_intensity": 0.85,
        "enhanced_emotional_profile": {
            "emotional_profile": {
                "fear": 0.85,
                "tension": 0.9,
                "dread": 0.8,
                "sadness": 0.7,
                "anger": 0.65,
                "reflection": 0.8,
                "curiosity": 0.6,
                "despair": 0.75,
                "paranoia": 0.8,
                "helplessness": 0.85
            },
            "emotional_arc": {
                "beginning": {
                    "curiosity": 0.7,
                    "tension": 0.6,
                    "unease": 0.7,
                    "confusion": 0.6
                },
                "middle": {
                    "fear": 0.8,
                    "tension": 0.9,
                    "hope": 0.4,
                    "paranoia": 0.8,
                    "rebellion": 0.5
                },
                "end": {
                    "dread": 0.9,
                    "despair": 0.8,
                    "reflection": 0.85,
                    "resignation": 0.9,
                    "emptiness": 0.85
                }
            },
            "emotional_keywords": [
                "disturbing",
                "chilling",
                "terrifying",
                "haunting",
                "unsettling",
                "thought-provoking",
                "oppressive",
                "claustrophobic",
                "bleak",
                "dystopian"
            ],
            "unexpected_emotions": [
                "hope",
                "tenderness",
                "defiance"
            ],
            "lasting_impact": "provokes deep reflection on freedom, truth, and the relationship between individuals and the state",
            "overall_emotional_profile": "creates a sense of mounting dread and paranoia that culminates in profound despair, leaving readers disturbed yet intellectually stimulated",
            "emotional_intensity": 0.85
        }
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "url": "https://www.goodreads.com/book/show/1885.Pride_and_Prejudice",
        "description": "Since its immediate success in 1813, Pride and Prejudice has remained one of the most popular novels in the English language. Jane Austen called this brilliant work 'her own darling child' and its vivacious heroine, Elizabeth Bennet, 'as delightful a creature as ever appeared in print.' The romantic clash between the opinionated Elizabeth and her proud beau, Mr. Darcy, is a splendid performance of civilized sparring. And Jane Austen's radiant wit sparkles as her characters dance a delicate quadrille of flirtation and intrigue, making this book the most superb comedy of manners of Regency England.",
        "genres": ["Fiction", "Classics", "Romance", "Historical Fiction"],
        "rating": 4.5,
        "reviews": [
            "A timeless classic with witty dialogue and memorable characters.",
            "Elizabeth Bennet is one of the most delightful heroines in literature.",
            "The romance between Elizabeth and Darcy is beautifully developed and satisfying.",
            "Austen's social commentary is as relevant today as it was in the 19th century.",
            "A perfect blend of romance, humor, and social observation."
        ],
        "reviews_data": {
            "book_id": "1885",
            "book_title": "Pride and Prejudice",
            "reviews": [
                {
                    "text": "A timeless classic with witty dialogue and memorable characters.",
                    "rating": 5,
                    "sentiment": 0.85
                },
                {
                    "text": "Elizabeth Bennet is one of the most delightful heroines in literature.",
                    "rating": 5,
                    "sentiment": 0.9
                },
                {
                    "text": "The romance between Elizabeth and Darcy is beautifully developed and satisfying.",
                    "rating": 4,
                    "sentiment": 0.8
                },
                {
                    "text": "Austen's social commentary is as relevant today as it was in the 19th century.",
                    "rating": 4,
                    "sentiment": 0.75
                },
                {
                    "text": "A perfect blend of romance, humor, and social observation.",
                    "rating": 5,
                    "sentiment": 0.85
                }
            ],
            "metadata": {
                "total_reviews": 5,
                "average_rating": 4.6,
                "average_sentiment": 0.83
            }
        },
        "emotional_profile": {
            "joy": 0.8,
            "amusement": 0.85,
            "satisfaction": 0.9,
            "hope": 0.7,
            "comfort": 0.75,
            "curiosity": 0.65,
            "tension": 0.5
        },
        "emotional_arc": {
            "beginning": {
                "amusement": 0.8,
                "curiosity": 0.7,
                "hope": 0.6
            },
            "middle": {
                "tension": 0.7,
                "frustration": 0.6,
                "hope": 0.5
            },
            "end": {
                "joy": 0.9,
                "satisfaction": 0.95,
                "comfort": 0.8
            }
        },
        "emotional_keywords": [
            "witty",
            "charming",
            "delightful",
            "romantic",
            "amusing",
            "satisfying"
        ],
        "emotional_intensity": 0.7,
        "enhanced_emotional_profile": {
            "emotional_profile": {
                "joy": 0.8,
                "amusement": 0.85,
                "satisfaction": 0.9,
                "hope": 0.7,
                "comfort": 0.75,
                "curiosity": 0.65,
                "tension": 0.5,
                "admiration": 0.8,
                "affection": 0.75,
                "indignation": 0.6
            },
            "emotional_arc": {
                "beginning": {
                    "amusement": 0.8,
                    "curiosity": 0.7,
                    "hope": 0.6,
                    "indignation": 0.5
                },
                "middle": {
                    "tension": 0.7,
                    "frustration": 0.6,
                    "hope": 0.5,
                    "embarrassment": 0.6,
                    "confusion": 0.5
                },
                "end": {
                    "joy": 0.9,
                    "satisfaction": 0.95,
                    "comfort": 0.8,
                    "relief": 0.7,
                    "affection": 0.85
                }
            },
            "emotional_keywords": [
                "witty",
                "charming",
                "delightful",
                "romantic",
                "amusing",
                "satisfying",
                "elegant",
                "spirited",
                "heartwarming",
                "clever"
            ],
            "unexpected_emotions": [
                "embarrassment",
                "indignation",
                "regret"
            ],
            "lasting_impact": "leaves readers with a warm sense of satisfaction and appreciation for the complexities of human relationships",
            "overall_emotional_profile": "offers a delightful journey from misunderstanding to mutual respect and love, filled with wit and social observation",
            "emotional_intensity": 0.7
        }
    }
]

def add_sample_data():
    """Add sample books with reviews and emotional profiles to the database."""
    try:
        db = MongoDBClient()
        
        # Check if sample books already exist
        existing_count = db.db.books.count_documents({
            "title": {"$in": [book["title"] for book in SAMPLE_BOOKS]}
        })
        
        if existing_count > 0:
            logger.info(f"Found {existing_count} sample books already in database")
            
            # Ask for confirmation to replace
            response = input(f"Replace {existing_count} existing sample books? (y/n): ")
            if response.lower() != 'y':
                logger.info("Operation cancelled by user")
                return
            
            # Delete existing sample books
            db.db.books.delete_many({
                "title": {"$in": [book["title"] for book in SAMPLE_BOOKS]}
            })
            logger.info(f"Deleted {existing_count} existing sample books")
        
        # Add sample books
        for book in SAMPLE_BOOKS:
            # Add timestamp
            book["created_at"] = datetime.now()
            book["last_emotional_analysis"] = datetime.now()
            
            # Add embedding (dummy for now)
            book["embedding"] = [0.0] * 384  # Dimension of all-MiniLM-L6-v2 embeddings
            
            # Insert book
            result = db.db.books.insert_one(book)
            logger.info(f"Added sample book: {book['title']} (ID: {result.inserted_id})")
        
        logger.info(f"Successfully added {len(SAMPLE_BOOKS)} sample books to database")
        
    except Exception as e:
        logger.error(f"Error adding sample data: {str(e)}")
        raise

def main():
    try:
        add_sample_data()
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 