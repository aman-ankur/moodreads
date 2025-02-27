import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.recommender.engine import RecommendationEngine
from moodreads.utils.logging_config import configure_logging

# Configure logging and silence warnings
configure_logging()

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
    search_query = selected_prompt if quick_search else query
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
                                    book = recommendations[i + j]
                                    with cols[j]:
                                        st.markdown('<div class="book-card">', unsafe_allow_html=True)
                                        
                                        # Title and author
                                        st.markdown(f'<h3 class="book-title">{book.get("title", "Unknown")}</h3>', unsafe_allow_html=True)
                                        st.markdown(f'<p class="book-author">by {book.get("author", "Unknown Author")}</p>', unsafe_allow_html=True)
                                        
                                        # Metadata
                                        st.markdown('<div class="book-metadata">', unsafe_allow_html=True)
                                        if book.get('rating'):
                                            st.markdown(f'<span class="rating">Rating: {book.get("rating")}</span>', unsafe_allow_html=True)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        # Genres
                                        if book.get('genres'):
                                            st.markdown(f'<p class="genres">Genres: {", ".join(book.get("genres", []))}</p>', unsafe_allow_html=True)
                                        
                                        # Description
                                        if book.get('description'):
                                            st.markdown(f'<p class="book-description">{book.get("description", "")[:200]}...</p>', unsafe_allow_html=True)
                                        
                                        # Link to book
                                        if book.get('url'):
                                            st.markdown(f'<a href="{book.get("url")}" target="_blank">View on Goodreads →</a>', unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again with a different query.") 