#!/usr/bin/env python3
"""
Script to check the database for books with emotional profiles and embeddings.
"""

import os
import sys
import logging
import traceback
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database():
    """Check the database for books with emotional profiles and embeddings."""
    try:
        print("Starting database check...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        
        # Import here to catch import errors
        try:
            from moodreads.database.mongodb import MongoDBClient
            print("Successfully imported MongoDBClient")
        except ImportError as e:
            print(f"Error importing MongoDBClient: {str(e)}")
            print(traceback.format_exc())
            return
        
        # Check if .env file exists
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_path):
            print(f".env file found at {env_path}")
        else:
            print(f".env file not found at {env_path}")
        
        # Connect to database
        try:
            print("Attempting to connect to MongoDB...")
            db = MongoDBClient()
            print(f"Connected to MongoDB: {db.db_name} at {db.mongodb_uri}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            print(traceback.format_exc())
            return
        
        # Count total books
        try:
            total_books = db.books_collection.count_documents({})
            print(f"Total books in database: {total_books}")
        except Exception as e:
            print(f"Error counting books: {str(e)}")
            print(traceback.format_exc())
        
        # Count books with emotional profiles
        try:
            books_with_profiles = db.books_collection.count_documents({'emotional_profile': {'$exists': True}})
            print(f"Books with emotional profiles: {books_with_profiles}")
        except Exception as e:
            print(f"Error counting books with profiles: {str(e)}")
            print(traceback.format_exc())
        
        # Count books with embeddings
        try:
            books_with_embeddings = db.books_collection.count_documents({'embedding': {'$exists': True}})
            print(f"Books with vector embeddings: {books_with_embeddings}")
        except Exception as e:
            print(f"Error counting books with embeddings: {str(e)}")
            print(traceback.format_exc())
        
        # Get a sample book with emotional profile
        if books_with_profiles > 0:
            try:
                sample_book = db.books_collection.find_one({'emotional_profile': {'$exists': True}})
                print("\nSample book with emotional profile:")
                print(f"Title: {sample_book.get('title', 'Unknown')}")
                print(f"Author: {sample_book.get('author', 'Unknown')}")
                
                # Print primary emotions
                primary_emotions = sample_book.get('emotional_profile', {}).get('primary_emotions', [])
                if primary_emotions:
                    print("\nPrimary emotions:")
                    for emotion in primary_emotions[:5]:  # Show first 5 emotions
                        print(f"- {emotion.get('emotion', 'Unknown')}: {emotion.get('intensity', 0)}")
                else:
                    print("\nNo primary emotions found in the emotional profile.")
            except Exception as e:
                print(f"Error retrieving sample book with profile: {str(e)}")
                print(traceback.format_exc())
        
        # Get a sample book with embedding
        if books_with_embeddings > 0:
            try:
                sample_book = db.books_collection.find_one({'embedding': {'$exists': True}})
                print("\nSample book with embedding:")
                print(f"Title: {sample_book.get('title', 'Unknown')}")
                print(f"Author: {sample_book.get('author', 'Unknown')}")
                
                # Print embedding info
                embedding = sample_book.get('embedding', [])
                if embedding:
                    print(f"Embedding dimensions: {len(embedding)}")
                    print(f"Embedding non-zero elements: {sum(1 for x in embedding if x > 0)}")
                    print(f"Embedding sample: {embedding[:5]}...")
                else:
                    print("Empty embedding vector.")
            except Exception as e:
                print(f"Error retrieving sample book with embedding: {str(e)}")
                print(traceback.format_exc())
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    check_database() 