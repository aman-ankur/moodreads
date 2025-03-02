"""
Configuration module for MoodReads application.
Contains feature flags and other configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Feature flags
FEATURES = {
    # Enable advanced recommendations
    "advanced_recommendations": os.getenv("ENABLE_ADVANCED_RECOMMENDATIONS", "true").lower() == "true",
    
    # Percentage of users to show advanced recommendations to (for A/B testing)
    "advanced_recommendations_percentage": int(os.getenv("ADVANCED_RECOMMENDATIONS_PERCENTAGE", "50")),
    
    # Enable detailed emotional profiles in recommendations
    "detailed_emotional_profiles": os.getenv("ENABLE_DETAILED_PROFILES", "true").lower() == "true",
}

# API configuration
API_CONFIG = {
    "version": "1.1.0",
    "default_recommendation_limit": 5,
    "max_recommendation_limit": 20,
}

# MongoDB configuration
MONGODB_CONFIG = {
    "uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017/moodreads"),
    "db_name": "moodreads",
    "collections": {
        "books": "books",
        "users": "users",
        "recommendations": "recommendations"
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 