/**
 * Advanced Recommendations Module
 * Handles the advanced recommendation features using emotional analysis
 */

import api from './api.js';
import AdvancedRecommendation from './components/AdvancedRecommendation.js';

class AdvancedRecommendationsManager {
  constructor() {
    this.resultsContainer = document.getElementById('recommendations-results');
    this.loadingIndicator = document.getElementById('loading-indicator');
    this.errorContainer = document.getElementById('error-message');
    this.moodInput = document.getElementById('mood-input');
    this.submitButton = document.getElementById('submit-button');
    this.advancedToggle = document.getElementById('advanced-toggle');
    this.favoriteBooks = new Set();
    
    this.bindEvents();
  }
  
  /**
   * Bind event listeners
   */
  bindEvents() {
    // If elements don't exist yet, they will be bound when the page loads
    if (this.submitButton) {
      this.submitButton.addEventListener('click', this.handleSubmit.bind(this));
    }
    
    if (this.moodInput) {
      this.moodInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.handleSubmit();
        }
      });
    }
    
    // Listen for DOM content loaded to ensure elements are available
    document.addEventListener('DOMContentLoaded', () => {
      this.resultsContainer = document.getElementById('recommendations-results');
      this.loadingIndicator = document.getElementById('loading-indicator');
      this.errorContainer = document.getElementById('error-message');
      this.moodInput = document.getElementById('mood-input');
      this.submitButton = document.getElementById('submit-button');
      this.advancedToggle = document.getElementById('advanced-toggle');
      
      if (this.submitButton) {
        this.submitButton.addEventListener('click', this.handleSubmit.bind(this));
      }
      
      if (this.moodInput) {
        this.moodInput.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') {
            this.handleSubmit();
          }
        });
      }
    });
  }
  
  /**
   * Handle form submission
   */
  async handleSubmit() {
    if (!this.moodInput || !this.moodInput.value.trim()) {
      this.showError('Please enter a mood');
      return;
    }
    
    const mood = this.moodInput.value.trim();
    const useAdvanced = this.advancedToggle && this.advancedToggle.checked;
    
    this.showLoading();
    this.clearResults();
    this.clearError();
    
    try {
      const recommendations = await this.getRecommendations(mood, useAdvanced);
      this.displayRecommendations(recommendations);
    } catch (error) {
      this.showError(error.message || 'Failed to get recommendations');
    } finally {
      this.hideLoading();
    }
  }
  
  /**
   * Get recommendations from the API
   * @param {string} mood - The mood query
   * @param {boolean} advanced - Whether to use advanced recommendations
   * @returns {Promise<Array>} - The recommendations
   */
  async getRecommendations(mood, advanced = true) {
    const options = {
      advanced: advanced,
      limit: 10
    };
    
    const response = await api.getRecommendations(mood, options);
    return response.recommendations || [];
  }
  
  /**
   * Display recommendations in the UI
   * @param {Array} recommendations - The recommendations to display
   */
  displayRecommendations(recommendations) {
    if (!this.resultsContainer) return;
    
    if (recommendations.length === 0) {
      this.showError('No recommendations found for this mood');
      return;
    }
    
    this.clearResults();
    
    recommendations.forEach(book => {
      const isFavorited = this.favoriteBooks.has(book.id);
      const recommendation = new AdvancedRecommendation(
        book,
        () => this.toggleFavorite(book.id),
        isFavorited
      );
      
      recommendation.render(this.resultsContainer);
    });
  }
  
  /**
   * Toggle a book as favorite
   * @param {string} bookId - The book ID
   */
  toggleFavorite(bookId) {
    if (this.favoriteBooks.has(bookId)) {
      this.favoriteBooks.delete(bookId);
    } else {
      this.favoriteBooks.add(bookId);
    }
    
    // Save favorites to localStorage
    localStorage.setItem('favoriteBooks', JSON.stringify([...this.favoriteBooks]));
  }
  
  /**
   * Load favorites from localStorage
   */
  loadFavorites() {
    try {
      const favorites = JSON.parse(localStorage.getItem('favoriteBooks')) || [];
      this.favoriteBooks = new Set(favorites);
    } catch (error) {
      console.error('Error loading favorites:', error);
      this.favoriteBooks = new Set();
    }
  }
  
  /**
   * Show loading indicator
   */
  showLoading() {
    if (this.loadingIndicator) {
      this.loadingIndicator.classList.remove('hidden');
    }
    
    if (this.submitButton) {
      this.submitButton.disabled = true;
    }
  }
  
  /**
   * Hide loading indicator
   */
  hideLoading() {
    if (this.loadingIndicator) {
      this.loadingIndicator.classList.add('hidden');
    }
    
    if (this.submitButton) {
      this.submitButton.disabled = false;
    }
  }
  
  /**
   * Show error message
   * @param {string} message - The error message
   */
  showError(message) {
    if (this.errorContainer) {
      this.errorContainer.textContent = message;
      this.errorContainer.classList.remove('hidden');
    }
  }
  
  /**
   * Clear error message
   */
  clearError() {
    if (this.errorContainer) {
      this.errorContainer.textContent = '';
      this.errorContainer.classList.add('hidden');
    }
  }
  
  /**
   * Clear results container
   */
  clearResults() {
    if (this.resultsContainer) {
      this.resultsContainer.innerHTML = '';
    }
  }
}

// Create and export a singleton instance
const recommendationsManager = new AdvancedRecommendationsManager();
export default recommendationsManager; 