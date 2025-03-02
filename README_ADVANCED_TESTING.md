# Testing Advanced Emotional Recommendations

This directory contains test scripts and tools for testing the advanced emotional recommendation system for MoodReads.

## Components

1. **Advanced Recommendation Algorithm** (`test_advanced_recommendations.py`)
   - Implements vector-based similarity for emotional matching
   - Provides more nuanced matching between mood queries and book emotional profiles
   - Includes detailed emotional information in recommendations

2. **Test API** (`test_api.py`)
   - FastAPI application for testing the advanced recommendation system
   - Provides an endpoint for getting advanced recommendations
   - Includes Pydantic models for request/response validation

3. **Test Client** (`test_client.html`)
   - Simple HTML/JavaScript client for testing the API
   - Allows testing different mood queries
   - Displays detailed emotional information for recommended books

## Testing Approach

The testing approach consists of three main steps:

1. **Algorithm Testing**
   - Test the advanced recommendation algorithm with various mood queries
   - Compare results with the original recommendation method
   - Analyze differences in recommendation quality and relevance

2. **API Testing**
   - Test the API endpoint for getting advanced recommendations
   - Verify request/response formats
   - Test error handling and edge cases

3. **UI Testing**
   - Test the client interface for usability
   - Verify that emotional information is displayed correctly
   - Test different mood queries and recommendation limits

## Running the Tests

To run all tests, use the provided shell script:

```bash
./run_tests.sh
```

This will:
1. Test the advanced recommendation algorithm
2. Compare it with the original method
3. Start the API server for manual testing

### Testing Individual Components

#### Algorithm Testing

```bash
python test_advanced_recommendations.py --mood "wonder and excitement" --output "results.json"
```

#### Comparison with Original Method

```bash
python test_advanced_recommendations.py --mood "wonder and excitement" --compare --output "comparison.json"
```

#### Running the API Server

```bash
python test_api.py
```

Then open `test_client.html` in your browser to test the API.

## Test Data

The tests use the existing book data in the MongoDB database. Make sure you have some books with emotional profiles in your database before running the tests.

## Expected Results

The advanced recommendation algorithm should provide:

1. More accurate emotional matching
2. More detailed emotional information
3. Better ranking of recommendations based on emotional similarity

The comparison with the original method should show:

1. Differences in book selection
2. Differences in ranking
3. Potential improvements in recommendation quality

## Troubleshooting

If you encounter issues:

1. Make sure MongoDB is running and accessible
2. Check that you have books with emotional profiles in your database
3. Verify that all required dependencies are installed
4. Check the logs for error messages 