# Goodreads Review Analysis

This tool analyzes Goodreads reviews extracted using the `extract_goodreads_reviews.py` script. It provides statistical analysis and visualizations to help understand reader sentiment and opinions.

## Features

- **Statistical Analysis**:
  - Average rating calculation
  - Word count statistics
  - Likes count analysis
  - Rating distribution

- **Sentiment Analysis**:
  - Polarity scores (negative to positive)
  - Subjectivity scores (objective to subjective)
  - Classification of reviews as positive, neutral, or negative

- **Visualizations**:
  - Word cloud of most frequent terms in reviews
  - Rating distribution chart
  - Sentiment analysis charts (distribution and metrics)

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Installation

1. Ensure you have Python installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install NLTK data (for word cloud generation):

```bash
python -m nltk.downloader stopwords
```

## Usage

Basic usage:

```bash
python analyze_reviews.py
```

This will:
- Load reviews from the default file (`goodreads_reviews.json`)
- Generate statistics and visualizations
- Save results to the `analysis_results` directory

### Command Line Arguments

- `--input`: Specify the input JSON file (default: `goodreads_reviews.json`)
- `--output-dir`: Specify the directory to save analysis results (default: `analysis_results`)

Example with custom input and output:

```bash
python analyze_reviews.py --input my_reviews.json --output-dir my_analysis
```

## Output

The script generates:

1. **Console Output**:
   - Basic statistics about the reviews
   - Sentiment analysis summary

2. **Files**:
   - `wordcloud.png`: Visual representation of most common words in reviews
   - `rating_distribution.png`: Bar chart showing the distribution of ratings
   - `sentiment_analysis.png`: Charts showing sentiment distribution and metrics
   - `review_stats.json`: JSON file containing all calculated statistics

## Interpreting Results

### Sentiment Analysis

- **Polarity**: Ranges from -1 (negative) to 1 (positive)
  - Values close to -1 indicate negative sentiment
  - Values close to 0 indicate neutral sentiment
  - Values close to 1 indicate positive sentiment

- **Subjectivity**: Ranges from 0 (objective) to 1 (subjective)
  - Values close to 0 indicate factual, objective content
  - Values close to 1 indicate personal opinions and subjective content

### Word Cloud

The word cloud shows the most frequent words in the reviews, with more common words appearing larger. Common English stopwords and book-related generic terms are filtered out to focus on meaningful content.

## Integration with MoodReads

This analysis tool complements the MoodReads recommendation system by providing deeper insights into reader emotions and opinions. The sentiment analysis can be particularly valuable for enhancing the emotional understanding of book reviews.

## Troubleshooting

- **Missing NLTK Data**: If you encounter errors related to NLTK data, run:
  ```bash
  python -m nltk.downloader stopwords
  ```

- **Matplotlib Backend Issues**: If you encounter problems with the matplotlib backend (especially on servers without a display), add the following to the top of your script:
  ```python
  import matplotlib
  matplotlib.use('Agg')
  ```

- **Empty Word Cloud**: This may occur if the reviews don't contain enough text after filtering stopwords. Try using a larger dataset of reviews.

## License

This project is open source under the MIT License. 