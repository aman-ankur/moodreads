from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import logging
import random
from integrate_emotional_analysis import BookDataIntegrator
from test_advanced_recommendations import get_advanced_mood_recommendations
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOGGING_CONFIG["level"]),
    format=config.LOGGING_CONFIG["format"]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
integrator = BookDataIntegrator()

@app.route('/')
def index():
    return render_template('index.html')

# New route for the advanced recommendations page
@app.route('/advanced')
def advanced_recommendations_page():
    """Render the advanced recommendations page with emotional analysis."""
    return render_template('advanced_recommendations.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    mood = request.form.get('mood')
    if not mood:
        return jsonify({'error': 'No mood provided'}), 400
    
    try:
        # Use the existing recommendation system
        recommendations = integrator.get_mood_recommendations(mood)
        # Render the results page with recommendations
        return render_template('results.html', mood=mood, recommendations=recommendations)
    except Exception as e:
        logger.error(f"Error in recommendation: {str(e)}")
        return render_template('results.html', mood=mood, recommendations=[], error=str(e))

# New endpoint for advanced recommendations
@app.route('/advanced-recommend', methods=['POST'])
def advanced_recommend():
    if not config.FEATURES["advanced_recommendations"]:
        # Fall back to original recommendations if feature is disabled
        return recommend()
    
    mood = request.form.get('mood')
    limit = request.form.get('limit', default=config.API_CONFIG["default_recommendation_limit"], type=int)
    limit = min(limit, config.API_CONFIG["max_recommendation_limit"])
    
    if not mood:
        return jsonify({'error': 'No mood provided'}), 400
    
    try:
        # Use the advanced recommendation system
        recommendations = get_advanced_mood_recommendations(integrator, mood, limit)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error in advanced recommendation: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API endpoint that accepts JSON for better integration with modern frontends
@app.route('/api/recommendations', methods=['POST'])
def api_recommendations():
    data = request.json
    if not data or 'mood' not in data:
        return jsonify({'error': 'No mood provided in request JSON'}), 400
    
    mood = data['mood']
    # Determine whether to use advanced recommendations
    use_advanced = data.get('advanced', False)
    
    # If not explicitly specified, use A/B testing based on configuration
    if 'advanced' not in data and config.FEATURES["advanced_recommendations"]:
        # Randomly assign users to advanced recommendations based on percentage
        use_advanced = random.randint(1, 100) <= config.FEATURES["advanced_recommendations_percentage"]
    
    limit = data.get('limit', config.API_CONFIG["default_recommendation_limit"])
    limit = min(limit, config.API_CONFIG["max_recommendation_limit"])
    
    try:
        if use_advanced and config.FEATURES["advanced_recommendations"]:
            # Use advanced recommendations
            logger.info(f"Using advanced recommendations for mood: {mood}")
            recommendations = get_advanced_mood_recommendations(integrator, mood, limit)
        else:
            # Use original recommendations
            logger.info(f"Using original recommendations for mood: {mood}")
            recommendations = integrator.get_mood_recommendations(mood, limit)
        
        # Add API version to response
        response = {
            "api_version": config.API_CONFIG["version"],
            "recommendations": recommendations,
            "advanced": use_advanced
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in API recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": config.API_CONFIG["version"],
        "features": {
            "advanced_recommendations": config.FEATURES["advanced_recommendations"],
            "detailed_emotional_profiles": config.FEATURES["detailed_emotional_profiles"]
        }
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    logger.info(f"Starting MoodReads API v{config.API_CONFIG['version']}")
    logger.info(f"Advanced recommendations: {'enabled' if config.FEATURES['advanced_recommendations'] else 'disabled'}")
    app.run(debug=True) 