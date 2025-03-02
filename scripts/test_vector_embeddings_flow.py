#!/usr/bin/env python3
"""
Test script for the vector embeddings flow.

This script tests the vector embeddings flow with different formats of emotional profiles,
ensuring that the VectorEmbeddingStore correctly handles various emotional profile formats.
"""

import os
import sys
import logging
import time
import json
import numpy as np
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
    from moodreads.analysis.vector_embeddings import VectorEmbeddingStore
    from moodreads.database.mongodb import MongoDB
except ImportError as e:
    logger.error(f"Error importing components: {str(e)}")
    sys.exit(1)

def test_vector_generation_with_dict_format():
    """Test vector generation with dictionary format emotional profile."""
    logger.info("Testing vector generation with dictionary format emotional profile...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_vector_test"
        db = MongoDB(db_name=db_name)
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Test with dictionary format emotional profile
        emotional_profile = {
            "joy": 0.8,
            "sadness": 0.2,
            "anger": 0.1,
            "fear": 0.3,
            "surprise": 0.4,
            "disgust": 0.1,
            "anticipation": 0.6,
            "trust": 0.7
        }
        
        # Generate vector
        vector = vector_store.generate_vector_from_dict_emotional_profile(emotional_profile)
        
        # Verify the vector
        if vector is not None and isinstance(vector, np.ndarray):
            logger.info(f"Vector successfully generated: shape={vector.shape}, non-zero elements={np.count_nonzero(vector)}")
            
            # Check specific values
            joy_index = vector_store.emotion_mappings.get("joy", -1)
            if joy_index >= 0 and joy_index < len(vector):
                logger.info(f"Joy value in vector: {vector[joy_index]}")
            
            return True
        else:
            logger.error("Vector generation failed")
            return False
        
    except Exception as e:
        logger.error(f"Error in vector generation with dictionary format: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_vector_generation_with_list_format():
    """Test vector generation with list format emotional profile."""
    logger.info("Testing vector generation with list format emotional profile...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_vector_test"
        db = MongoDB(db_name=db_name)
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Test with list format emotional profile
        emotional_profile = [
            {"emotion": "joy", "score": 0.8},
            {"emotion": "sadness", "score": 0.2},
            {"emotion": "anger", "score": 0.1},
            {"emotion": "fear", "score": 0.3},
            {"emotion": "surprise", "score": 0.4},
            {"emotion": "disgust", "score": 0.1},
            {"emotion": "anticipation", "score": 0.6},
            {"emotion": "trust", "score": 0.7}
        ]
        
        # Generate vector
        vector = vector_store.generate_vector_from_list_emotional_profile(emotional_profile)
        
        # Verify the vector
        if vector is not None and isinstance(vector, np.ndarray):
            logger.info(f"Vector successfully generated: shape={vector.shape}, non-zero elements={np.count_nonzero(vector)}")
            
            # Check specific values
            joy_index = vector_store.emotion_mappings.get("joy", -1)
            if joy_index >= 0 and joy_index < len(vector):
                logger.info(f"Joy value in vector: {vector[joy_index]}")
            
            return True
        else:
            logger.error("Vector generation failed")
            return False
        
    except Exception as e:
        logger.error(f"Error in vector generation with list format: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_process_book_with_dict_format():
    """Test processing a book with dictionary format emotional profile."""
    logger.info("Testing process_book with dictionary format emotional profile...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_vector_test"
        db = MongoDB(db_name=db_name)
        
        # Clear existing data for clean test
        db.books_collection.delete_many({"_id": "test_dict_format"})
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Create a test book with dictionary format emotional profile
        test_book = {
            "_id": "test_dict_format",
            "title": "Test Book with Dict Format",
            "author": "Test Author",
            "url": "https://www.goodreads.com/book/show/test_dict_format",
            "emotional_analysis": {
                "joy": 0.8,
                "sadness": 0.2,
                "anger": 0.1,
                "fear": 0.3,
                "surprise": 0.4,
                "disgust": 0.1,
                "anticipation": 0.6,
                "trust": 0.7
            }
        }
        
        # Insert the test book
        db.books_collection.insert_one(test_book)
        
        # Process the book for vectors
        vector_store.process_book_for_vectors(test_book)
        
        # Verify the book has vector embeddings
        updated_book = db.books_collection.find_one({"_id": "test_dict_format"})
        
        if updated_book and updated_book.get('vector_embedding') is not None:
            logger.info(f"Book successfully processed for vectors: {updated_book.get('title')}")
            
            # Check the vector embedding
            vector_embedding = updated_book.get('vector_embedding')
            if isinstance(vector_embedding, list) and len(vector_embedding) > 0:
                logger.info(f"Vector embedding: length={len(vector_embedding)}")
                return True
            else:
                logger.error("Vector embedding is empty or invalid")
                return False
        else:
            logger.error("Book was not updated with vector embeddings")
            return False
        
    except Exception as e:
        logger.error(f"Error in process_book with dictionary format: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_process_book_with_list_format():
    """Test processing a book with list format emotional profile."""
    logger.info("Testing process_book with list format emotional profile...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_vector_test"
        db = MongoDB(db_name=db_name)
        
        # Clear existing data for clean test
        db.books_collection.delete_many({"_id": "test_list_format"})
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Create a test book with list format emotional profile
        test_book = {
            "_id": "test_list_format",
            "title": "Test Book with List Format",
            "author": "Test Author",
            "url": "https://www.goodreads.com/book/show/test_list_format",
            "emotional_analysis": [
                {"emotion": "joy", "score": 0.8},
                {"emotion": "sadness", "score": 0.2},
                {"emotion": "anger", "score": 0.1},
                {"emotion": "fear", "score": 0.3},
                {"emotion": "surprise", "score": 0.4},
                {"emotion": "disgust", "score": 0.1},
                {"emotion": "anticipation", "score": 0.6},
                {"emotion": "trust", "score": 0.7}
            ]
        }
        
        # Insert the test book
        db.books_collection.insert_one(test_book)
        
        # Process the book for vectors
        vector_store.process_book_for_vectors(test_book)
        
        # Verify the book has vector embeddings
        updated_book = db.books_collection.find_one({"_id": "test_list_format"})
        
        if updated_book and updated_book.get('vector_embedding') is not None:
            logger.info(f"Book successfully processed for vectors: {updated_book.get('title')}")
            
            # Check the vector embedding
            vector_embedding = updated_book.get('vector_embedding')
            if isinstance(vector_embedding, list) and len(vector_embedding) > 0:
                logger.info(f"Vector embedding: length={len(vector_embedding)}")
                return True
            else:
                logger.error("Vector embedding is empty or invalid")
                return False
        else:
            logger.error("Book was not updated with vector embeddings")
            return False
        
    except Exception as e:
        logger.error(f"Error in process_book with list format: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_vector_operations():
    """Test vector operations like normalization and cosine similarity."""
    logger.info("Testing vector operations...")
    
    try:
        # Initialize database with test name
        db_name = "moodreads_vector_test"
        db = MongoDB(db_name=db_name)
        
        # Initialize vector store
        vector_store = VectorEmbeddingStore(db_instance=db)
        
        # Test vector normalization
        test_vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        normalized_vector = vector_store.normalize_vector(test_vector)
        
        # Verify normalization
        norm = np.linalg.norm(normalized_vector)
        if abs(norm - 1.0) < 1e-6:  # Check if norm is close to 1
            logger.info(f"Vector normalization successful: norm={norm}")
        else:
            logger.error(f"Vector normalization failed: norm={norm}")
            return False
        
        # Test cosine similarity
        vector1 = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0, 0.0, 0.0])
        vector3 = np.array([1.0, 1.0, 0.0, 0.0, 0.0])
        
        # Orthogonal vectors should have similarity 0
        similarity1 = vector_store.cosine_similarity(vector1, vector2)
        if abs(similarity1) < 1e-6:
            logger.info(f"Cosine similarity for orthogonal vectors: {similarity1}")
        else:
            logger.error(f"Cosine similarity for orthogonal vectors incorrect: {similarity1}")
            return False
        
        # Same vector should have similarity 1
        similarity2 = vector_store.cosine_similarity(vector1, vector1)
        if abs(similarity2 - 1.0) < 1e-6:
            logger.info(f"Cosine similarity for same vector: {similarity2}")
        else:
            logger.error(f"Cosine similarity for same vector incorrect: {similarity2}")
            return False
        
        # Vector3 is at 45 degrees to vector1, so similarity should be 1/sqrt(2)
        similarity3 = vector_store.cosine_similarity(vector1, vector3)
        expected = 1.0 / np.sqrt(2.0)
        if abs(similarity3 - expected) < 1e-6:
            logger.info(f"Cosine similarity for 45-degree vectors: {similarity3}")
        else:
            logger.error(f"Cosine similarity for 45-degree vectors incorrect: {similarity3}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error in vector operations: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function."""
    try:
        logger.info("Starting vector embeddings flow tests")
        start_time = time.time()
        
        # Track test results
        results = []
        
        # Run tests
        dict_format_success = test_vector_generation_with_dict_format()
        results.append(("Vector Generation with Dict Format", dict_format_success))
        
        list_format_success = test_vector_generation_with_list_format()
        results.append(("Vector Generation with List Format", list_format_success))
        
        process_dict_success = test_process_book_with_dict_format()
        results.append(("Process Book with Dict Format", process_dict_success))
        
        process_list_success = test_process_book_with_list_format()
        results.append(("Process Book with List Format", process_list_success))
        
        vector_ops_success = test_vector_operations()
        results.append(("Vector Operations", vector_ops_success))
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("VECTOR EMBEDDINGS FLOW TEST RESULTS")
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
        logger.error(f"Error during vector embeddings flow tests: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 