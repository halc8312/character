/**
 * Character Database - Graph Visualization
 * Uses Cytoscape.js for interactive relationship graph
 */

const GraphApp = {
  cy: null,
  layout: {},
  newNodes: new Set(),
  
  /**
   * Initialize Cytoscape graph
   */
  initGraph(container, nodes, edges, savedLayout) {
    this.layout = savedLayout || {};
    this.newNodes = new Set();
    
    // Find nodes without saved positions
    nodes.forEach(node => {
      if (!this.layout[node.id]) {
        this.newNodes.add(node.id);
      }
    });
    
    // Convert to Cytoscape format
    const cyNodes = nodes.map(node => {
      const savedPos = this.layout[node.id];
      return {
        data: {
          id: node.id,
          label: node.label,
          tags: node.tags || []
        },
        position: savedPos ? { x: savedPos.x, y: savedPos.y } : undefined,
        locked: savedPos ? true : false
      };
    });
    
    const cyEdges = edges.map(edge => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.type,
        intensity: edge.intensity || 3,
        summary: edge.summary || '',
        tags: edge.tags || []
      }
    }));
    
    this.cy = cytoscape({
      container: container,
      elements: {
        nodes: cyNodes,
        edges: cyEdges
      },
      style: this.getStyles(),
      layout: { name: 'preset' },
      wheelSensitivity: 0.3,
      minZoom: 0.2,
      maxZoom: 3
    });
    
    // Position new nodes and run partial layout
    this.positionNewNodes();
    
    return this.cy;
  },
  
  /**
   * Get Cytoscape styles
   */
  getStyles() {
    return [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'text-valign': 'bottom',
          'text-halign': 'center',
          'text-margin-y': 8,
          'font-size': '12px',
          'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          'background-color': '#4a6fa5',
          'width': 40,
          'height': 40,
          'border-width': 2,
          'border-color': '#3d5a80'
        }
      },
      {
        selector: 'node.highlighted',
        style: {
          'background-color': '#e8b04a',
          'border-color': '#c9a227',
          'border-width': 3,
          'width': 50,
          'height': 50,
          'z-index': 999
        }
      },
      {
        selector: 'node.new',
        style: {
          'background-color': '#66bb6a',
          'border-color': '#4caf50'
        }
      },
      {
        selector: 'node.dimmed',
        style: {
          'opacity': 0.3
        }
      },
      {
        selector: 'node.hidden',
        style: {
          'display': 'none'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 'mapData(intensity, 1, 5, 1, 4)',
          'line-color': '#999',
          'curve-style': 'bezier',
          'target-arrow-shape': 'none',
          'opacity': 0.7
        }
      },
      {
        selector: 'edge.highlighted',
        style: {
          'line-color': '#e8b04a',
          'width': 4,
          'opacity': 1,
          'z-index': 999
        }
      },
      {
        selector: 'edge.dimmed',
        style: {
          'opacity': 0.15
        }
      },
      {
        selector: 'edge.hidden',
        style: {
          'display': 'none'
        }
      },
      // Edge type colors
      {
        selector: 'edge[type="friend"]',
        style: { 'line-color': '#4caf50' }
      },
      {
        selector: 'edge[type="rival"]',
        style: { 'line-color': '#f44336' }
      },
      {
        selector: 'edge[type="enemy"]',
        style: { 'line-color': '#b71c1c' }
      },
      {
        selector: 'edge[type="lover"], edge[type="crush"], edge[type="ex_lover"]',
        style: { 'line-color': '#e91e63' }
      },
      {
        selector: 'edge[type="sibling"], edge[type="parent"], edge[type="child"], edge[type="spouse"], edge[type="relative"]',
        style: { 'line-color': '#9c27b0' }
      },
      {
        selector: 'edge[type="mentor"], edge[type="student"]',
        style: { 'line-color': '#2196f3' }
      },
      {
        selector: 'edge[type="colleague"], edge[type="partner"]',
        style: { 'line-color': '#607d8b' }
      }
    ];
  },
  
  /**
   * Position new nodes and run partial layout
   */
  positionNewNodes() {
    if (this.newNodes.size === 0) return;
    
    const existingBounds = this.getExistingNodesBounds();
    const newNodeIds = Array.from(this.newNodes);
    
    // Place new nodes in a grid near the existing graph
    const gridSize = Math.ceil(Math.sqrt(newNodeIds.length));
    const spacing = 100;
    const startX = existingBounds.x2 + spacing;
    const startY = existingBounds.y1;
    
    newNodeIds.forEach((nodeId, index) => {
      const node = this.cy.getElementById(nodeId);
      if (node.length > 0) {
        const row = Math.floor(index / gridSize);
        const col = index % gridSize;
        node.position({
          x: startX + col * spacing,
          y: startY + row * spacing
        });
        node.addClass('new');
      }
    });
    
    // Run partial layout on new nodes + their neighbors
    this.runPartialLayout();
  },
  
  /**
   * Get bounds of existing (positioned) nodes
   */
  getExistingNodesBounds() {
    const existingNodes = this.cy.nodes().filter(node => !this.newNodes.has(node.id()));
    
    if (existingNodes.length === 0) {
      return { x1: 0, y1: 0, x2: 0, y2: 0 };
    }
    
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    existingNodes.forEach(node => {
      const pos = node.position();
      minX = Math.min(minX, pos.x);
      minY = Math.min(minY, pos.y);
      maxX = Math.max(maxX, pos.x);
      maxY = Math.max(maxY, pos.y);
    });
    
    return { x1: minX, y1: minY, x2: maxX, y2: maxY };
  },
  
  /**
   * Run partial layout on new nodes
   */
  runPartialLayout() {
    if (this.newNodes.size === 0) return;
    
    // Get new nodes and their direct neighbors
    const newNodeElements = this.cy.nodes().filter(node => this.newNodes.has(node.id()));
    const neighbors = newNodeElements.neighborhood('node');
    const elementsToLayout = newNodeElements.union(neighbors);
    
    // Lock existing nodes
    this.cy.nodes().forEach(node => {
      if (!this.newNodes.has(node.id())) {
        node.lock();
      }
    });
    
    // Run cose layout on the subset
    const layout = elementsToLayout.layout({
      name: 'cose',
      animate: false,
      randomize: false,
      fit: false,
      padding: 50,
      nodeRepulsion: function() { return 8000; },
      idealEdgeLength: function() { return 100; },
      edgeElasticity: function() { return 100; },
      nestingFactor: 1.2,
      gravity: 0.25,
      numIter: 200
    });
    
    layout.run();
    
    // Unlock all nodes
    this.cy.nodes().unlock();
  },
  
  /**
   * Run full layout on all nodes
   */
  runFullLayout() {
    // Unlock all nodes first
    this.cy.nodes().unlock();
    
    const layout = this.cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 1000,
      randomize: true,
      fit: true,
      padding: 50,
      nodeRepulsion: function() { return 10000; },
      idealEdgeLength: function() { return 120; },
      edgeElasticity: function() { return 100; },
      nestingFactor: 1.2,
      gravity: 0.3,
      numIter: 500
    });
    
    layout.run();
    
    // Clear new nodes indicator after full layout
    this.cy.nodes().removeClass('new');
    this.newNodes.clear();
  },
  
  /**
   * Export current layout as JSON
   */
  exportLayout() {
    const layoutData = {};
    
    this.cy.nodes().forEach(node => {
      const pos = node.position();
      layoutData[node.id()] = {
        x: Math.round(pos.x * 100) / 100,
        y: Math.round(pos.y * 100) / 100
      };
    });
    
    return layoutData;
  },
  
  /**
   * Download layout as JSON file
   */
  downloadLayout() {
    const layoutData = this.exportLayout();
    const json = JSON.stringify(layoutData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'layout.json';
    a.click();
    
    URL.revokeObjectURL(url);
  },
  
  /**
   * Search and highlight node
   */
  searchAndHighlight(query) {
    // Clear previous highlights
    this.cy.elements().removeClass('highlighted dimmed');
    
    if (!query || !query.trim()) {
      return null;
    }
    
    const q = query.toLowerCase().trim();
    
    // Find matching nodes
    const matchingNodes = this.cy.nodes().filter(node => {
      const label = (node.data('label') || '').toLowerCase();
      const id = (node.id() || '').toLowerCase();
      return label.includes(q) || id.includes(q);
    });
    
    if (matchingNodes.length > 0) {
      // Highlight matches
      matchingNodes.addClass('highlighted');
      
      // Dim other elements
      this.cy.elements().not(matchingNodes).not(matchingNodes.connectedEdges()).addClass('dimmed');
      
      // Focus on first match
      const firstMatch = matchingNodes[0];
      this.cy.animate({
        center: { eles: firstMatch },
        zoom: 1.5
      }, { duration: 300 });
      
      return firstMatch;
    }
    
    return null;
  },
  
  /**
   * Focus on a specific node by ID
   */
  focusNode(nodeId) {
    const node = this.cy.getElementById(nodeId);
    
    if (node.length > 0) {
      // Clear and highlight
      this.cy.elements().removeClass('highlighted dimmed');
      node.addClass('highlighted');
      node.connectedEdges().addClass('highlighted');
      
      // Animate to node
      this.cy.animate({
        center: { eles: node },
        zoom: 1.5
      }, { duration: 500 });
      
      return node;
    }
    
    return null;
  },
  
  /**
   * Show only neighbors of selected node (1-hop or 2-hop)
   */
  showNeighborsOnly(nodeId, hops = 1) {
    const node = this.cy.getElementById(nodeId);
    if (node.length === 0) return;
    
    this.cy.elements().removeClass('dimmed hidden');
    
    let visible = node;
    
    for (let i = 0; i < hops; i++) {
      const neighbors = visible.neighborhood();
      visible = visible.union(neighbors);
    }
    
    const connectedEdges = visible.connectedEdges();
    visible = visible.union(connectedEdges);
    
    // Dim non-visible elements
    this.cy.elements().not(visible).addClass('dimmed');
  },
  
  /**
   * Reset visibility
   */
  resetVisibility() {
    this.cy.elements().removeClass('highlighted dimmed hidden');
  },
  
  /**
   * Filter by tags
   */
  filterByTags(activeTags, type = 'node') {
    if (!activeTags || activeTags.length === 0) {
      this.cy.nodes().removeClass('hidden');
      this.cy.edges().removeClass('hidden');
      return;
    }
    
    this.cy.nodes().forEach(node => {
      const nodeTags = node.data('tags') || [];
      const hasTag = activeTags.some(tag => nodeTags.includes(tag));
      
      if (hasTag) {
        node.removeClass('hidden');
      } else {
        node.addClass('hidden');
      }
    });
    
    // Hide edges connected to hidden nodes
    this.cy.edges().forEach(edge => {
      const source = edge.source();
      const target = edge.target();
      
      if (source.hasClass('hidden') || target.hasClass('hidden')) {
        edge.addClass('hidden');
      } else {
        edge.removeClass('hidden');
      }
    });
  },
  
  /**
   * Filter by relationship types
   */
  filterByRelationTypes(activeTypes) {
    if (!activeTypes || activeTypes.length === 0) {
      this.cy.edges().removeClass('hidden');
      return;
    }
    
    this.cy.edges().forEach(edge => {
      const edgeType = edge.data('type');
      
      if (activeTypes.includes(edgeType)) {
        edge.removeClass('hidden');
      } else {
        edge.addClass('hidden');
      }
    });
  },
  
  /**
   * Get unique relationship types from graph
   */
  getRelationshipTypes() {
    const types = new Set();
    this.cy.edges().forEach(edge => {
      types.add(edge.data('type'));
    });
    return Array.from(types).sort();
  },
  
  /**
   * Get new nodes count
   */
  getNewNodesCount() {
    return this.newNodes.size;
  }
};

// Export for use in graph.html
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GraphApp;
}
