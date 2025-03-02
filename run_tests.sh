#!/bin/bash

# Run tests for vector-based recommendations

echo "=== Testing Vector Embeddings ==="
echo "Running test with sample emotional profile..."
python test_vector_embeddings.py

echo ""
echo "=== Testing Mood Recommendations ==="
echo "Getting recommendations for 'wonder and excitement'..."
python test_vector_embeddings.py --mood "wonder and excitement" --output "test_wonder_excitement.json"

echo ""
echo "=== Starting API Server ==="
echo "Starting the API server on port 8001..."
echo "Once the server is running, you can test it using the test_client.html file."
echo "Press Ctrl+C to stop the server when done."
python -m uvicorn test_api:app --host 0.0.0.0 --port 8001 --reload 