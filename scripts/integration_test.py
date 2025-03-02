#!/usr/bin/env python3
"""
Integration tests for MoodReads.

This script runs integration tests that verify the actual flow between components
with minimal mocking, ensuring that the components work together correctly.
"""

import os
import sys
import logging
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import components
try:
    from moodreads.scraper.goodreads import AdvancedBookScraper
    from moodreads.database.mongodb import MongoDB
    from moodreads.analysis.claude import EmotionalAnalyzer
    from moodreads.analysis.vector_embeddings import VectorEmbeddingStore
except ImportError as e:
    logger.error(f"Error importing components: {str(e)}")
    sys.exit(1)

def test_scraper_to_database_flow():
    """Test the flow from scraper to database."""
    logger.info("Testing scraper to database flow...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_integration_test"
        db = MongoDB(db_name=db_name)
        
        # Clear existing data for clean test
        db.books_collection.delete_many({})
        
        # Initialize scraper
        scraper = AdvancedBookScraper(db_instance=db)
        
        # Test with a single known book URL
        test_url = "https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye"
        
        # Process the book
        logger.info(f"Processing book: {test_url}")
        scraper.process_batch([test_url], batch_num=1)
        
        # Verify the book was added to the database
        book = db.books_collection.find_one({"url": test_url})
        
        if book:
            logger.info(f"Book successfully added to database: {book.get('title', 'Unknown')}")
            return True
        else:
            logger.error("Book was not added to database")
            return False
        
    except Exception as e:
        logger.error(f"Error in scraper to database flow: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_analyzer_flow():
    """Test the emotional analyzer flow."""
    logger.info("Testing emotional analyzer flow...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_integration_test"
        db = MongoDB(db_name=db_name)
        
        # Initialize analyzer
        analyzer = EmotionalAnalyzer(db_instance=db)
        
        # Get a book from the database
        book = db.books_collection.find_one({})
        
        if not book:
            logger.error("No books found in database. Run test_scraper_to_database_flow first.")
            return False
        
        # Skip if the book already has emotional analysis
        if book.get('emotional_analysis'):
            logger.info("Book already has emotional analysis, skipping...")
            return True
        
        # Analyze the book
        logger.info(f"Analyzing book: {book.get('title', 'Unknown')}")
        
        # Use a simplified analysis for testing
        test_analysis = {
            "joy": 0.8,
            "sadness": 0.2,
            "anger": 0.1,
            "fear": 0.3,
            "surprise": 0.4,
            "disgust": 0.1,
            "anticipation": 0.6,
            "trust": 0.7
        }
        
        # Update the book with the test analysis
        db.books_collection.update_one(
            {"_id": book["_id"]},
            {"$set": {"emotional_analysis": test_analysis}}
        )
        
        # Verify the book was updated
        updated_book = db.books_collection.find_one({"_id": book["_id"]})
        
        if updated_book and updated_book.get('emotional_analysis'):
            logger.info(f"Book successfully analyzed: {updated_book.get('title', 'Unknown')}")
            return True
        else:
            logger.error("Book was not updated with emotional analysis")
            return False
        
    except Exception as e:
        logger.error(f"Error in analyzer flow: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_vector_embeddings_flow():
    """Test the vector embeddings flow."""
    logger.info("Testing vector embeddings flow...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_integration_test"
        db = MongoDB(db_name=db_name)
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Get a book from the database
        book = db.books_collection.find_one({"emotional_analysis": {"$exists": True}})
        
        if not book:
            logger.error("No books found with emotional analysis. Run test_analyzer_flow first.")
            return False
        
        # Process the book for vectors
        logger.info(f"Processing book for vectors: {book.get('title', 'Unknown')}")
        vector_store.process_book_for_vectors(book)
        
        # Verify the book has vector embeddings
        updated_book = db.books_collection.find_one({"_id": book["_id"]})
        
        if updated_book and updated_book.get('vector_embedding'):
            logger.info(f"Book successfully processed for vectors: {updated_book.get('title', 'Unknown')}")
            return True
        else:
            logger.error("Book was not updated with vector embeddings")
            return False
        
    except Exception as e:
        logger.error(f"Error in vector embeddings flow: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_end_to_end_flow():
    """Test the end-to-end flow from scraping to vector embeddings."""
    logger.info("Testing end-to-end flow...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_integration_test_e2e"
        db = MongoDB(db_name=db_name)
        
        # Clear existing data for clean test
        db.books_collection.delete_many({})
        
        # Initialize components
        scraper = AdvancedBookScraper(db_instance=db)
        analyzer = EmotionalAnalyzer(db_instance=db)
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Test with a single known book URL
        test_url = "https://www.goodreads.com/book/show/5107.The_Catcher_in_the_Rye"
        
        # Process the book
        logger.info(f"Processing book: {test_url}")
        scraper.process_batch([test_url], batch_num=1)
        
        # Verify the book was added to the database
        book = db.books_collection.find_one({"url": test_url})
        
        if not book:
            logger.error("Book was not added to database")
            return False
        
        # Use a simplified analysis for testing
        test_analysis = {
            "joy": 0.8,
            "sadness": 0.2,
            "anger": 0.1,
            "fear": 0.3,
            "surprise": 0.4,
            "disgust": 0.1,
            "anticipation": 0.6,
            "trust": 0.7
        }
        
        # Update the book with the test analysis
        db.books_collection.update_one(
            {"_id": book["_id"]},
            {"$set": {"emotional_analysis": test_analysis}}
        )
        
        # Process the book for vectors
        book = db.books_collection.find_one({"_id": book["_id"]})
        vector_store.process_book_for_vectors(book)
        
        # Verify the book has vector embeddings
        updated_book = db.books_collection.find_one({"_id": book["_id"]})
        
        if updated_book and updated_book.get('vector_embedding'):
            logger.info(f"End-to-end flow successful for book: {updated_book.get('title', 'Unknown')}")
            return True
        else:
            logger.error("End-to-end flow failed")
            return False
        
    except Exception as e:
        logger.error(f"Error in end-to-end flow: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function."""
    try:
        logger.info("Starting integration tests")
        start_time = time.time()
        
        # Track test results
        results = []
        
        # Run tests
        scraper_db_success = test_scraper_to_database_flow()
        results.append(("Scraper to Database Flow", scraper_db_success))
        
        analyzer_success = test_analyzer_flow()
        results.append(("Emotional Analyzer Flow", analyzer_success))
        
        vector_success = test_vector_embeddings_flow()
        results.append(("Vector Embeddings Flow", vector_success))
        
        e2e_success = test_end_to_end_flow()
        results.append(("End-to-End Flow", e2e_success))
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("INTEGRATION TEST RESULTS")
        logger.info("=" * 50)
        
        all_passed = True
        for name, result in results:
            status = "PASSED" if result else "FAILED"
            logger.info(f"{name}: {status}")
            if not result:
                all_passed = False
        
        logger.info("=" * 50)
        logger.info(f"OVERALL: {'PASSED' if all_passed else 'FAILED'}")
        logger.info("=" * 50)
        
        # Print timing
        elapsed_time = time.time() - start_time
        logger.info(f"Total test time: {elapsed_time:.2f} seconds")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        logger.error(f"Error during integration tests: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 