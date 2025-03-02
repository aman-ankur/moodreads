/**
 * MoodReads API Client
 * Handles communication with the MoodReads backend API
 */

class MoodReadsAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.endpoints = {
            recommendations: '/api/recommendations',
            health: '/api/health'
        };
    }

    /**
     * Get book recommendations based on mood
     * 
     * @param {string} mood - The mood query
     * @param {Object} options - Additional options
     * @param {boolean} options.advanced - Whether to use advanced recommendations
     * @param {number} options.limit - Maximum number of recommendations to return
     * @returns {Promise<Object>} - The recommendations response
     */
    async getRecommendations(mood, options = {}) {
        const url = this.baseUrl + this.endpoints.recommendations;
        
        const requestData = {
            mood: mood,
            ...options
        };
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            throw error;
        }
    }
    
    /**
     * Check API health status
     * 
     * @returns {Promise<Object>} - The health status response
     */
    async checkHealth() {
        const url = this.baseUrl + this.endpoints.health;
        
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }
}

// Create and export a singleton instance
const api = new MoodReadsAPI();
export default api; 