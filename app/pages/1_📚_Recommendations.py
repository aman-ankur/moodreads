import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import html

from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.recommender.engine import RecommendationEngine
from moodreads.utils.logging_config import configure_logging

# Configure logging and silence warnings
configure_logging()

def transform_book_data(book):
    """Transform raw book data into a properly formatted structure for UI rendering."""
    # Extract and sanitize basic fields with HTML escaping
    title = html.escape(str(book.get("title", "Unknown")).strip())
    author = html.escape(str(book.get("author", "Unknown Author")).strip())
    
    # Handle rating conversion safely
    try:
        rating_val = float(book.get("rating", 0))
        rating = f"{rating_val:.2f}" if rating_val > 0 else ""
    except (ValueError, TypeError):
        rating = ""
    
    # Clean other basic fields
    year = str(book.get("year", "")).strip()
    isbn = str(book.get("isbn", "0")).strip()
    url = str(book.get("url", "")).strip()
    
    # Process description - remove common prefixes and clean up
    description = str(book.get("description", "")).strip()
    if description:
        # Remove common prefixes like "From Goodreads:" or "Book description:"
        prefixes_to_remove = ["From Goodreads:", "Book description:", "Description:"]
        for prefix in prefixes_to_remove:
            if description.lower().startswith(prefix.lower()):
                description = description[len(prefix):].strip()
        # Split on "readers." and take the latter part if it exists
        if "readers." in description:
            parts = description.split("readers.", 1)
            if len(parts) > 1:
                description = parts[1].strip()
    
    # Process genres - ensure it's a list and clean up
    genres = book.get("genres", [])
    if isinstance(genres, str):
        genres = [g.strip() for g in genres.split(",")]
    elif not isinstance(genres, list):
        genres = []
    
    # Clean up genres list - remove empty/None values and ensure strings
    genres = [str(g).strip() for g in genres if g and str(g).strip()]
    
    return {
        "title": title,
        "author": author,
        "rating": rating,
        "year": year,
        "isbn": isbn,
        "url": url,
        "description": description,
        "genres": genres
    }

# Load custom CSS
def load_css():
    with open(Path(__file__).parent.parent / "styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Pre-made prompts
SAMPLE_PROMPTS = {
    "Mood Lifting": [
        "I want an uplifting and inspiring book that will make me feel hopeful",
        "Looking for a heartwarming story that will make me smile",
        "Need a book that will boost my mood and motivation"
    ],
    "Relaxation": [
        "I'm feeling anxious and need something calming and peaceful",
        "Want a gentle, soothing story to help me unwind",
        "Looking for a book that's like a warm hug"
    ],
    "Adventure": [
        "I want an exciting adventure that will help me escape reality",
        "Looking for a thrilling story full of action and suspense",
        "Need an epic journey that will keep me on the edge of my seat"
    ],
    "Personal Growth": [
        "I want a book that will help me understand myself better",
        "Looking for wisdom and insights about life",
        "Need inspiration for personal transformation"
    ]
}

# Page config
st.set_page_config(
    page_title="MoodReads - Book Recommendations",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
load_css()

# Initialize components
@st.cache_resource
def get_analyzer():
    return EmotionalAnalyzer(use_cache=True)

@st.cache_resource
def get_recommender():
    return RecommendationEngine()

analyzer = get_analyzer()
recommender = get_recommender()

# Hero section
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <h1>Find Your Perfect Book Match</h1>
        <p class="hero-description">Tell us how you're feeling or choose from our pre-made prompts, and we'll find books that match your emotional needs.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content
tab1, tab2 = st.tabs(["✨ Quick Start", "🎯 Custom Search"])

with tab1:
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown("### Choose a Pre-made Prompt")
    st.markdown('<p class="section-description">Select a category and prompt that matches your current mood or reading desire:</p>', unsafe_allow_html=True)
    
    selected_category = st.selectbox(
        "What kind of experience are you looking for?",
        options=list(SAMPLE_PROMPTS.keys()),
        index=0
    )
    
    selected_prompt = st.radio(
        "Choose a prompt:",
        options=SAMPLE_PROMPTS[selected_category],
        index=0
    )

    # Add custom prompt input
    st.markdown("### Add Your Own Touch (Optional)")
    custom_addition = st.text_area(
        "Add any specific preferences or requirements:",
        placeholder="Example: I prefer books with happy endings, or I like books set in historical periods",
        help="This will be combined with the selected prompt to better match your preferences"
    )
    
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        num_recommendations = st.slider(
            "Number of recommendations",
            min_value=1,
            max_value=20,
            value=5,
            label_visibility="visible"
        )
    with col3:
        final_prompt = selected_prompt
        if custom_addition:
            final_prompt = f"{selected_prompt}. Additional preferences: {custom_addition}"
        quick_search = st.button(
            "🔍 Find Books",
            type="primary",
            key="quick_search",
            use_container_width=True,
            help="Click to find book recommendations"
        )
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown("### Craft Your Own Query")
    st.markdown('<p class="section-description">Describe your emotional needs or the kind of book you\'re looking for:</p>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        query = st.text_area(
            "What kind of book are you looking for?",
            height=100,
            placeholder="Examples:\n• I want an uplifting and inspiring book that will make me feel hopeful\n• I'm feeling anxious and need something calming and peaceful\n• Looking for an exciting adventure that will help me escape reality",
            key="custom_search"
        )
        
        # Additional preferences
        preferences = st.text_area(
            "Any specific preferences?",
            placeholder="Example: I prefer books with strong female leads, or I like books that are part of a series",
            help="Add any specific preferences to help us find better matches"
        )
        
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            custom_num_recommendations = st.slider(
                "Number of recommendations",
                min_value=1,
                max_value=20,
                value=5,
                key="custom_slider",
                label_visibility="visible"
            )
        with col3:
            final_custom_query = query
            if preferences:
                final_custom_query = f"{query}. Additional preferences: {preferences}"
            custom_search = st.button(
                "🔍 Find Books",
                type="primary",
                key="custom_search_btn",
                use_container_width=True,
                help="Click to find book recommendations"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Process search
if quick_search or (custom_search and query):
    search_query = final_prompt if quick_search else final_custom_query
    num_results = num_recommendations if quick_search else custom_num_recommendations
    
    if not search_query:
        st.warning("⚠️ Please enter your query or select a pre-made prompt!")
    else:
        with st.spinner("🔍 Analyzing your query and finding the perfect books..."):
            try:
                # Get emotional profile
                emotional_profile, embedding = analyzer.analyze(search_query)
                
                # Get recommendations
                recommendations = recommender.get_recommendations(
                    emotional_profile,
                    search_query,
                    limit=num_results
                )
                
                if not recommendations:
                    st.warning("📚 No matching books found. Try a different query!")
                else:
                    # Create tabs for results
                    results_tab1, results_tab2 = st.tabs(["📚 Recommendations", "🎯 Emotional Analysis"])
                    
                    with results_tab2:
                        st.markdown('<div class="emotion-chart">', unsafe_allow_html=True)
                        # Create emotion profile chart
                        emotions_df = pd.DataFrame({
                            'Emotion': list(emotional_profile.keys()),
                            'Score': list(emotional_profile.values())
                        })
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=emotions_df['Emotion'],
                            y=emotions_df['Score'],
                            marker_color='#1e88e5',
                            opacity=0.8
                        ))
                        
                        fig.update_layout(
                            title={
                                'text': 'Emotional Analysis of Your Query',
                                'y':0.95,
                                'x':0.5,
                                'xanchor': 'center',
                                'yanchor': 'top'
                            },
                            xaxis_title='Emotion',
                            yaxis_title='Score',
                            yaxis_range=[0, 1],
                            template='plotly_white',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.info("""
                        This chart shows how our AI interpreted your query's emotional content.
                        Higher scores indicate stronger emotional associations.
                        """)
                    
                    with results_tab1:
                        st.markdown('<h2 class="section-title">📚 Recommended Books</h2>', unsafe_allow_html=True)
                        
                        # Display recommendations in a grid
                        for i in range(0, len(recommendations), 2):
                            cols = st.columns(2)
                            for j in range(2):
                                if i + j < len(recommendations):
                                    # Transform raw book data
                                    raw_book = recommendations[i + j]
                                    book = transform_book_data(raw_book)
                                    
                                    with cols[j]:
                                        # First render the book card structure with proper escaping
                                        st.markdown(f"""
                                        <div class="book-card">
                                            <div class="book-card-content">
                                                <div class="book-cover-container">
                                                    <img src="https://covers.openlibrary.org/b/isbn/{book['isbn']}-M.jpg" 
                                                         alt="{book['title']}"
                                                         onerror="this.onerror=null; this.src='https://via.placeholder.com/200x300?text=No+Cover';"
                                                         class="book-cover">
                                                </div>
                                                <div class="book-details">
                                                    <h3 class="book-title">{book['title']}</h3>
                                                    <p class="book-author">by {book['author']}</p>
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Then render metadata separately with proper checks
                                        if book['rating'] or book['year']:
                                            metadata_parts = []
                                            if book['rating']:
                                                metadata_parts.append(f'<span class="rating">★ {book["rating"]}</span>')
                                            if book['year']:
                                                metadata_parts.append(f'<span class="book-year">{book["year"]}</span>')
                                            
                                            st.markdown(
                                                f'<div class="book-metadata">{" ".join(metadata_parts)}</div>',
                                                unsafe_allow_html=True
                                            )
                                        
                                        # Render genres with proper checks
                                        if book['genres']:
                                            st.markdown(
                                                f'<div class="book-genres">{", ".join(book["genres"])}</div>',
                                                unsafe_allow_html=True
                                            )
                                        
                                        # Use native Streamlit components for interactive elements
                                        col1, col2 = st.columns([1, 1])
                                        with col1:
                                            if book['description']:
                                                with st.expander("Read Description"):
                                                    st.write(book['description'])
                                        with col2:
                                            if book['url']:
                                                st.markdown(
                                                    f'''<div class="book-actions">
                                                        <a href="{book['url']}" target="_blank" class="action-button view-on-goodreads">
                                                            View on Goodreads
                                                        </a>
                                                    </div>''',
                                                    unsafe_allow_html=True
                                                )
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again with a different query.") 