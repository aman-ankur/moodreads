/**
 * AdvancedRecommendation Component
 * Displays a book recommendation with detailed emotional information
 */

class AdvancedRecommendation {
  /**
   * Create a new AdvancedRecommendation component
   * @param {Object} book - The book recommendation data
   * @param {string} book.title - Book title
   * @param {string} book.author - Book author
   * @param {string} book.coverUrl - URL to book cover image
   * @param {number} book.matchScore - Match score as percentage
   * @param {Array} book.matchingEmotions - Array of matching emotions
   * @param {Object} book.emotionalArc - Emotional arc of the book
   * @param {string} book.overallProfile - Overall emotional profile
   * @param {Function} onFavorite - Callback when favorite button is clicked
   * @param {boolean} isFavorited - Whether the book is favorited
   */
  constructor(book, onFavorite = null, isFavorited = false) {
    this.book = book;
    this.onFavorite = onFavorite;
    this.isFavorited = isFavorited;
    this.element = this._createElement();
  }

  /**
   * Create the DOM element for the component
   * @private
   * @returns {HTMLElement} The component element
   */
  _createElement() {
    const container = document.createElement('div');
    container.className = 'card hover:shadow-lg transition-shadow mb-6';
    
    // Create the main content
    container.innerHTML = `
      <div class="flex gap-6 p-4">
        <!-- Book Cover -->
        <div class="relative w-32 h-48 flex-shrink-0">
          <img 
            src="${this.book.coverUrl || '/images/default-cover.jpg'}" 
            alt="Cover of ${this.book.title}" 
            class="object-cover rounded-lg shadow-md w-full h-full"
          />
        </div>

        <!-- Book Info -->
        <div class="flex-1 space-y-4">
          <div class="flex justify-between items-start">
            <div>
              <h3 class="font-serif text-xl">${this.book.title}</h3>
              <p class="text-text/70">${this.book.author}</p>
            </div>
            ${this.onFavorite ? `
              <button class="favorite-btn p-2 hover:bg-button-pink/20 rounded-full transition-colors">
                <svg class="w-6 h-6 ${this.isFavorited ? 'fill-accent stroke-accent' : 'stroke-text/50'}" 
                  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
              </button>
            ` : ''}
          </div>

          <!-- Emotional Match -->
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <div class="h-2 flex-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-button-green transition-all duration-500"
                  style="width: ${this.book.matchScore}%"
                />
              </div>
              <span class="text-sm font-medium text-text/70">
                ${this.book.matchScore}% match
              </span>
            </div>
            ${this.book.overallProfile ? `
              <p class="text-sm text-text/80">${this.book.overallProfile}</p>
            ` : ''}
          </div>
          
          <!-- Matching Emotions -->
          <div class="space-y-2">
            <h4 class="text-sm font-medium">Matching Emotions</h4>
            <div class="flex flex-wrap gap-2">
              ${this.book.matchingEmotions?.map(emotion => `
                <span class="px-2 py-1 bg-button-green/10 text-button-green text-xs rounded-full">
                  ${emotion.emotion}: ${emotion.intensity}/10
                </span>
              `).join('') || ''}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Emotional Details (Expandable) -->
      <div class="emotional-details hidden px-4 pb-4 pt-0">
        ${this.book.emotionalArc ? `
          <div class="border-t border-gray-200 pt-4 mt-2">
            <h4 class="text-sm font-medium mb-2">Emotional Arc</h4>
            <div class="grid grid-cols-3 gap-4">
              ${Object.entries(this.book.emotionalArc).map(([stage, emotions]) => `
                <div>
                  <h5 class="text-xs font-medium capitalize">${stage}</h5>
                  <ul class="text-xs text-text/70">
                    ${emotions.slice(0, 3).map(emotion => `
                      <li>${emotion}</li>
                    `).join('')}
                  </ul>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
      
      <!-- Toggle Button -->
      <button class="toggle-details w-full text-center py-2 text-sm text-text/50 hover:text-text/70 border-t border-gray-200">
        Show emotional details
      </button>
    `;
    
    // Add event listeners
    const toggleBtn = container.querySelector('.toggle-details');
    const detailsSection = container.querySelector('.emotional-details');
    
    toggleBtn.addEventListener('click', () => {
      const isHidden = detailsSection.classList.contains('hidden');
      detailsSection.classList.toggle('hidden', !isHidden);
      toggleBtn.textContent = isHidden ? 'Hide emotional details' : 'Show emotional details';
    });
    
    if (this.onFavorite) {
      const favoriteBtn = container.querySelector('.favorite-btn');
      favoriteBtn.addEventListener('click', () => {
        this.isFavorited = !this.isFavorited;
        const icon = favoriteBtn.querySelector('svg');
        if (this.isFavorited) {
          icon.classList.add('fill-accent', 'stroke-accent');
          icon.classList.remove('stroke-text/50');
        } else {
          icon.classList.remove('fill-accent', 'stroke-accent');
          icon.classList.add('stroke-text/50');
        }
        this.onFavorite();
      });
    }
    
    return container;
  }

  /**
   * Render the component into a container element
   * @param {HTMLElement} container - The container to render into
   */
  render(container) {
    container.appendChild(this.element);
  }
  
  /**
   * Update the component with new data
   * @param {Object} book - New book data
   */
  update(book) {
    this.book = book;
    const newElement = this._createElement();
    this.element.replaceWith(newElement);
    this.element = newElement;
  }
}

// Export the component
export default AdvancedRecommendation; 