/**
 * Document Outline Component
 * Displays hierarchical table of contents from AST
 */

import React, { useState, useCallback } from 'react';
import { OutlineItem } from '../services/documentService';

interface DocumentOutlineProps {
  outline: OutlineItem[];
  onItemClick: (nodeId: string) => void;
  currentNodeId?: string | null;
}

const DocumentOutline: React.FC<DocumentOutlineProps> = ({
  outline,
  onItemClick,
  currentNodeId,
}) => {
  const [collapsedItems, setCollapsedItems] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  // Filter outline based on search term
  const filteredOutline = outline.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Toggle collapse state
  const toggleCollapse = useCallback((itemId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setCollapsedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  }, []);

  // Handle item click
  const handleItemClick = useCallback((itemId: string) => {
    onItemClick(itemId);
  }, [onItemClick]);

  // Get visible items (considering collapsed state)
  const getVisibleItems = () => {
    const visibleItems: OutlineItem[] = [];
    const stack: { item: OutlineItem; parentCollapsed: boolean }[] = 
      filteredOutline.map(item => ({ item, parentCollapsed: false }));

    while (stack.length > 0) {
      const { item, parentCollapsed } = stack.shift()!;
      
      if (!parentCollapsed) {
        visibleItems.push(item);
      }

      // Check if this item should show its children
      const isCollapsed = collapsedItems.has(item.id);
      const childrenHidden = parentCollapsed || isCollapsed;

      // Add children to stack (they'll be processed in order)
      const children = filteredOutline.filter(child => 
        child.depth === item.depth + 1 && 
        filteredOutline.indexOf(child) > filteredOutline.indexOf(item)
      );

      children.forEach(child => {
        stack.unshift({ item: child, parentCollapsed: childrenHidden });
      });
    }

    return visibleItems;
  };

  const visibleItems = getVisibleItems();

  // Get item class names
  const getItemClassName = (item: OutlineItem) => {
    const baseClass = 'outline-item';
    const levelClass = `outline-level-${item.level}`;
    const depthClass = `outline-depth-${item.depth}`;
    const activeClass = currentNodeId === item.id ? 'active' : '';
    const collapsedClass = collapsedItems.has(item.id) ? 'collapsed' : '';
    
    return [baseClass, levelClass, depthClass, activeClass, collapsedClass]
      .filter(Boolean)
      .join(' ');
  };

  // Check if item has children
  const hasChildren = (item: OutlineItem) => {
    return outline.some(other => 
      other.depth === item.depth + 1 && 
      outline.indexOf(other) > outline.indexOf(item)
    );
  };

  // Get indentation style
  const getIndentationStyle = (depth: number) => ({
    paddingLeft: `${depth * 16 + 8}px`,
  });

  return (
    <div className="document-outline">
      <div className="outline-header">
        <h3>Document Outline</h3>
        <div className="outline-stats">
          {outline.length} headings
        </div>
      </div>

      <div className="outline-search">
        <input
          type="text"
          placeholder="Search headings..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="outline-search-input"
        />
      </div>

      <div className="outline-content">
        {visibleItems.length === 0 ? (
          <div className="outline-empty">
            {searchTerm ? (
              <p>No headings match "{searchTerm}"</p>
            ) : (
              <p>No headings found</p>
            )}
          </div>
        ) : (
          <ul className="outline-list">
            {visibleItems.map((item) => (
              <li
                key={item.id}
                className={getItemClassName(item)}
                style={getIndentationStyle(item.depth)}
              >
                <div className="outline-item-content">
                  {hasChildren(item) && (
                    <button
                      className="outline-toggle"
                      onClick={(e) => toggleCollapse(item.id, e)}
                      title={collapsedItems.has(item.id) ? 'Expand' : 'Collapse'}
                    >
                      {collapsedItems.has(item.id) ? '▶' : '▼'}
                    </button>
                  )}
                  
                  <button
                    className="outline-link"
                    onClick={() => handleItemClick(item.id)}
                    title={`Go to: ${item.title}`}
                  >
                    <span className="outline-level-indicator">
                      H{item.level}
                    </span>
                    <span className="outline-title">
                      {searchTerm ? (
                        <span
                          dangerouslySetInnerHTML={{
                            __html: item.title.replace(
                              new RegExp(`(${searchTerm})`, 'gi'),
                              '<mark>$1</mark>'
                            ),
                          }}
                        />
                      ) : (
                        item.title
                      )}
                    </span>
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="outline-footer">
        <div className="outline-actions">
          <button
            className="outline-action"
            onClick={() => setCollapsedItems(new Set())}
            title="Expand all"
          >
            Expand All
          </button>
          <button
            className="outline-action"
            onClick={() => setCollapsedItems(new Set(outline.map(item => item.id)))}
            title="Collapse all"
          >
            Collapse All
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentOutline;
