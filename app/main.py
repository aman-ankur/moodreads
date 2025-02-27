import streamlit as st
from pathlib import Path

# Load custom CSS
def load_css():
    with open(Path(__file__).parent / "styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="MoodReads",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
load_css()

# Hero section with improved visibility
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <img src="https://em-content.zobj.net/source/skype/289/books_1f4da.png" alt="Books" class="hero-icon">
        <h1>Welcome to MoodReads</h1>
        <p class="hero-description">Find books that match your emotional state and reading preferences</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Search input section
st.markdown("""
<div class="search-container">
    <h2>What kind of book are you looking for?</h2>
</div>
""", unsafe_allow_html=True)

query = st.text_area(
    "",
    placeholder="Examples:\n• I want an uplifting and inspiring book that will make me feel hopeful\n• I'm feeling anxious and need something calming and peaceful\n• Looking for an exciting adventure that will help me escape reality",
    height=100
)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🔍 Find Books", type="primary", use_container_width=True):
        if query:
            st.session_state['search_query'] = query
            st.switch_page("pages/recommendations.py")
        else:
            st.warning("Please enter your query first!")

# Features section with improved visibility
st.markdown('<h2 class="section-title">✨ How It Works</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <h3>Emotional Matching</h3>
        <p>Our AI understands your emotional needs and finds books that match your current state of mind.</p>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Smart Analysis</h3>
        <p>We analyze both your query and our book database using advanced natural language processing.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <h3>Personalized Results</h3>
        <p>Get book recommendations tailored to your specific emotional needs and preferences.</p>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <h3>Match Scoring</h3>
        <p>See how well each book matches your requirements with our detailed scoring system.</p>
    </div>
    """, unsafe_allow_html=True)

# Sample prompts section
st.markdown('<h2 class="section-title">💡 Example Queries</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="examples-grid">
    <div class="example-card">
        "I want an uplifting and inspiring book that will make me feel hopeful"
    </div>
    <div class="example-card">
        "Looking for a calming story to help me relax after a stressful day"
    </div>
    <div class="example-card">
        "Need an exciting adventure to escape from reality"
    </div>
    <div class="example-card">
        "Want a book that will help me understand myself better"
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>MoodReads - Your Emotional Book Discovery Platform</p>
</div>
""", unsafe_allow_html=True) 