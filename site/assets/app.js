/**
 * Character Database - Shared JavaScript
 * Handles data fetching, search, and tag filtering
 */

const App = {
  data: {
    characters: [],
    graph: { nodes: [], edges: [] },
    layout: {}
  },
  
  /**
   * Fetch JSON data from the data directory
   */
  async fetchData(filename) {
    try {
      const response = await fetch(`data/${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load ${filename}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching ${filename}:`, error);
      return null;
    }
  },
  
  /**
   * Load all data files
   */
  async loadAllData() {
    const [characters, graph, layout] = await Promise.all([
      this.fetchData('characters.json'),
      this.fetchData('graph.json'),
      this.fetchData('layout.json')
    ]);
    
    this.data.characters = characters || [];
    this.data.graph = graph || { nodes: [], edges: [] };
    this.data.layout = layout || {};
    
    return this.data;
  },
  
  /**
   * Extract unique tags by prefix
   */
  extractTagsByPrefix(characters, prefix) {
    const tags = new Set();
    characters.forEach(char => {
      (char.tags || []).forEach(tag => {
        if (tag.startsWith(prefix + '/')) {
          tags.add(tag);
        }
      });
    });
    return Array.from(tags).sort();
  },
  
  /**
   * Extract all unique tag prefixes
   */
  extractTagPrefixes(characters) {
    const prefixes = new Set();
    characters.forEach(char => {
      (char.tags || []).forEach(tag => {
        const parts = tag.split('/');
        if (parts.length >= 2) {
          prefixes.add(parts[0]);
        }
      });
    });
    return Array.from(prefixes).sort();
  },
  
  /**
   * Search characters by text
   */
  searchCharacters(characters, query) {
    if (!query || !query.trim()) {
      return characters;
    }
    
    const q = query.toLowerCase().trim();
    return characters.filter(char => {
      // Search in name_display
      if (char.name_display && char.name_display.toLowerCase().includes(q)) {
        return true;
      }
      // Search in name_romanized
      if (char.name_romanized && char.name_romanized.toLowerCase().includes(q)) {
        return true;
      }
      // Search in id
      if (char.id && char.id.toLowerCase().includes(q)) {
        return true;
      }
      // Search in aliases
      if (char.aliases && char.aliases.some(a => a.toLowerCase().includes(q))) {
        return true;
      }
      return false;
    });
  },
  
  /**
   * Filter characters by tags
   */
  filterByTags(characters, activeTags) {
    if (!activeTags || activeTags.length === 0) {
      return characters;
    }
    
    return characters.filter(char => {
      const charTags = char.tags || [];
      return activeTags.some(tag => charTags.includes(tag));
    });
  },
  
  /**
   * Get character by ID
   */
  getCharacterById(id) {
    return this.data.characters.find(c => c.id === id);
  },
  
  /**
   * Get edges connected to a character
   */
  getCharacterEdges(characterId) {
    return this.data.graph.edges.filter(
      e => e.source === characterId || e.target === characterId
    );
  },
  
  /**
   * Get node label by ID
   */
  getNodeLabel(nodeId) {
    const node = this.data.graph.nodes.find(n => n.id === nodeId);
    return node ? node.label : nodeId;
  },
  
  /**
   * Get URL query parameter
   */
  getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  },
  
  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
  
  /**
   * Create tag element HTML
   */
  createTagHtml(tag) {
    const escaped = this.escapeHtml(tag);
    let className = 'tag';
    if (tag.startsWith('role/')) {
      className += ' role';
    } else if (tag.startsWith('faction/')) {
      className += ' faction';
    } else if (tag.startsWith('trait/')) {
      className += ' trait';
    }
    return `<span class="${className}">${escaped}</span>`;
  },
  
  /**
   * Format intensity as visual indicator
   */
  formatIntensity(intensity) {
    if (intensity === undefined || intensity === null) return '';
    const value = Math.max(-5, Math.min(5, intensity));
    const absValue = Math.abs(value);
    let symbol = value >= 0 ? '★' : '☆';
    return symbol.repeat(absValue) + (value !== 0 ? ` (${value})` : '');
  },
  
  /**
   * Debounce function for search input
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = App;
}
