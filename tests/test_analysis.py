import pytest
from moodreads.analysis.claude import EmotionalAnalyzer

def test_emotional_analyzer_initialization():
    analyzer = EmotionalAnalyzer()
    assert analyzer is not None

def test_analyze_text():
    analyzer = EmotionalAnalyzer()
    text = "A heartwarming story about family reconciliation"
    profile, embedding = analyzer.analyze(text)
    
    assert isinstance(profile, dict)
    assert 'joy' in profile
    assert 'comfort' in profile
    assert len(embedding) == 384  # MiniLM embedding dimension 