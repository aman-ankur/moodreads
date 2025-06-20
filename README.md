# Moodreads 📚

Moodreads is an emotional book recommendation system that matches readers with books based on their emotional needs rather than traditional genre categories. Using advanced NLP and emotional analysis, it helps readers find books that resonate with their current emotional state and desires.

## Features 🌟

- **Emotional Analysis**: Uses Claude AI to analyze emotional content of books and user requests
- **Smart Recommendations**: Hybrid recommendation system combining:
  - Emotional profile matching
  - Vector similarity search
  - Rule-based filtering
- **Book Data Collection**: Ethical scraping of book information from Goodreads and Google Books API
- **User Management**: JWT-based authentication and user preferences
- **Web Interface**: Clean, intuitive Streamlit interface

## Architecture 🏗️ 

Moodreads follows a modular architecture with clear separation of concerns:

### Data Collection Layer
- **GoodreadsScraper**: Ethically scrapes book metadata, reviews, and ratings from Goodreads
- **GoogleBooksAPIClient**: Retrieves additional book data including descriptions, categories, and publisher information
- **BookDataIntegrator**: Merges data from multiple sources to create comprehensive book records

### Emotional Analysis Layer
- **EmotionalAnalyzer**: Processes book descriptions and reviews to extract emotional signals
  - Identifies primary emotions with intensity scores (1-10)
  - Maps emotional arcs (beginning, middle, end)
  - Extracts lasting impact emotions and unexpected emotional elements
  - Generates emotional keywords and phrases
- **VectorEmbeddingStore**: Converts emotional profiles into vector representations
  - Maps emotions to positions in a fixed-dimension vector space
  - Normalizes vectors for fair comparisons
  - Enables efficient similarity searches

### Data Storage Layer
- **MongoDB**: Stores book metadata, emotional profiles, and vector embeddings
  - Flexible document structure for complex emotional data
  - Efficient indexing for similarity searches
  - Collections for books, users, and recommendation history

### Recommendation Engine
- **Hybrid Retrieval-Augmented Generation**:
  1. LLM translates emotional prompts into search parameters
  2. Vector similarity search finds emotionally matching books
  3. Final ranking based on multidimensional emotional similarity
  4. Results include explanation of emotional matching

## Enhanced Emotional Analysis 🧠

Our advanced emotional analysis system goes beyond simple sentiment analysis:

### Comprehensive Emotional Dimensions
- **Primary Emotions**: Joy, sadness, tension, comfort, wonder, fear, etc. with intensity scores
- **Emotional Arcs**: Progression of feelings throughout the book (beginning, middle, end)
- **Lasting Impact**: Emotions that linger after finishing the book
- **Unexpected Elements**: Surprising emotional moments that subvert expectations

### Vector-Based Emotional Fingerprinting
- Each book receives a unique emotional vector embedding
- Emotions are mapped to specific dimensions in vector space
- Similar emotional experiences cluster together in this space
- Enables nuanced matching beyond simple genre categorization

### Multi-Source Analysis
- Combines signals from book descriptions, reviews, and genre information
- Weights different sources appropriately (reviews > descriptions > genres)
- Creates a holistic view of the emotional experience a book provides

## Getting Started 🚀

Follow these steps to set up and run the Moodreads application on your local machine:

### Prerequisites

- Python 3.9+ 
- Node.js 16+ and npm
- MongoDB 4.4+
- Anthropic API key (for Claude AI)
- Google Books API key (optional, for enhanced metadata)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/moodreads.git
cd moodreads
```

2. **Set up Python environment**

```bash
# Create and activate virtual environment
python -m venv .moodreads-env
source .moodreads-env/bin/activate  # On Windows: .moodreads-env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

3. **Set up MongoDB**

```bash
# Start MongoDB (if not running as a service)
mongod --dbpath /path/to/data/db

# Create database (in another terminal)
mongo
> use moodreads
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```
CLAUDE_API_KEY=your_claude_api_key
MONGODB_URI=mongodb://localhost:27017/moodreads
JWT_SECRET=your_jwt_secret_key
GOODREADS_SCRAPER_DELAY=3.0
GOOGLE_BOOKS_API_KEY=your_google_books_api_key
LOG_LEVEL=INFO
```

### Running the Application

1. **Populate the database with books**

```bash
# Run the scraper to collect a small set of books (for testing)
python scripts/test_advanced_scraper.py --category science-fiction --num-books 5

# For a larger dataset, run the full scraper
python scripts/scrape_books.py --categories fiction science-fiction --depth 2
```

2. **Start the backend API**

```bash
# Start the FastAPI backend
cd backend
uvicorn main:app --reload --port 8000
```

3. **Start the frontend**

```bash
# In a new terminal, navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

4. **Access the application**

Open your browser and navigate to:
- Frontend: http://localhost:3000
- API documentation: http://localhost:8000/docs

### Testing Recommendations

1. **Try sample mood queries**:
   - "I'm feeling anxious and need something calming"
   - "I want an exciting adventure that will make me forget my problems"
   - "Looking for a book that will make me feel hopeful about the future"

2. **View book emotional profiles**:
   - Navigate to any book detail page to see its emotional analysis
   - Compare recommendations to understand the matching algorithm

### Troubleshooting

- **API Connection Issues**: Ensure MongoDB is running and accessible
- **Empty Recommendations**: Check that books have been scraped and analyzed
- **Claude API Errors**: Verify your API key and quota limits
- **Scraper Timeouts**: Adjust rate limiting in the `.env` file

## Contributing 🤝

We welcome contributions to Moodreads! Here's how you can help:

1. **Report bugs and suggest features** by opening issues
2. **Submit pull requests** for bug fixes or new features
3. **Improve documentation** to help others understand the project
4. **Share feedback** on the emotional analysis accuracy

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines for Python code
- Use Google-style docstrings for documentation
- Include type hints for all function parameters and return values
- Write unit tests for new functionality
