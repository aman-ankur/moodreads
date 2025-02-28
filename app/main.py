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

# Add Get Started button using Streamlit's button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/1_📚_Recommendations.py")

# Featured Books Grid
st.markdown('<h2 class="section-title">📚 Featured Books</h2>', unsafe_allow_html=True)

featured_books = [
    {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "image": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1559986152i/386162.jpg"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "image": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1657781256i/61439040.jpg"
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "image": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1320399351i/1885.jpg"
    },
    {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "image": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1566425108i/33.jpg"
    }
]

# Create a grid of featured books
cols = st.columns(4)
for idx, book in enumerate(featured_books):
    with cols[idx]:
        st.markdown(f"""
        <div class="featured-book-card">
            <img src="{book['image']}" alt="{book['title']}" class="book-cover">
            <h3>{book['title']}</h3>
            <p>{book['author']}</p>
        </div>
        """, unsafe_allow_html=True)

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