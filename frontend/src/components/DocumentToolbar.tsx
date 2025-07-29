/**
 * Document Toolbar Component
 * Provides document-level actions and search functionality
 */

import React, { useState, useCallback } from 'react';
import { Document } from '../services/documentService';

interface DocumentToolbarProps {
  document: Document | null;
  onSearch: (term: string) => void;
  onSave: () => Promise<void>;
  onToggleOutline: () => void;
  onRawEdit: () => void;
  showOutline: boolean;
  isDirty: boolean;
  lastSaved: Date | null;
}

const DocumentToolbar: React.FC<DocumentToolbarProps> = ({
  document,
  onSearch,
  onSave,
  onToggleOutline,
  onRawEdit,
  showOutline,
  isDirty,
  lastSaved,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  // Handle search input
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    onSearch(term);
  }, [onSearch]);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!isDirty || isSaving) return;
    
    setIsSaving(true);
    try {
      await onSave();
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setIsSaving(false);
    }
  }, [isDirty, isSaving, onSave]);

  // Handle export
  const handleExport = useCallback((format: 'markdown' | 'html') => {
    if (!document) return;
    
    // This would trigger export functionality
    console.log(`Exporting document as ${format}`);
    setShowExportMenu(false);
  }, [document]);

  // Format last saved time
  const formatLastSaved = () => {
    if (!lastSaved) return 'Never saved';
    
    const now = new Date();
    const diff = now.getTime() - lastSaved.getTime();
    
    if (diff < 60000) { // Less than 1 minute
      return 'Just saved';
    } else if (diff < 3600000) { // Less than 1 hour
      const minutes = Math.floor(diff / 60000);
      return `Saved ${minutes}m ago`;
    } else {
      return `Saved at ${lastSaved.toLocaleTimeString()}`;
    }
  };

  return (
    <div className="document-toolbar">
      <div className="toolbar-left">
        <button
          className={`toolbar-btn ${showOutline ? 'active' : ''}`}
          onClick={onToggleOutline}
          title="Toggle outline"
        >
          📋 Outline
        </button>

        <button
          className="toolbar-btn"
          onClick={onRawEdit}
          title="Edit raw markdown"
        >
          📝 Raw Edit
        </button>
        
        <div className="search-container">
          <input
            type="text"
            placeholder="Search document..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
          />
          {searchTerm && (
            <button
              className="search-clear"
              onClick={() => {
                setSearchTerm('');
                onSearch('');
              }}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="toolbar-center">
        {document && (
          <div className="document-info">
            <span className="document-title">{document.title}</span>
            <div className="document-stats">
              <span>{document.metadata.wordCount} words</span>
              <span>•</span>
              <span>{document.metadata.pageCount} pages</span>
              <span>•</span>
              <span>{document.metadata.nodeCount} blocks</span>
            </div>
          </div>
        )}
      </div>

      <div className="toolbar-right">
        <div className="save-status">
          <span className={`save-indicator ${isDirty ? 'dirty' : 'clean'}`}>
            {isDirty ? '●' : '✓'}
          </span>
          <span className="save-text">
            {formatLastSaved()}
          </span>
        </div>

        <button
          className={`toolbar-btn save-btn ${isDirty ? 'dirty' : ''}`}
          onClick={handleSave}
          disabled={!isDirty || isSaving}
          title="Save document (Ctrl+S)"
        >
          {isSaving ? '💾 Saving...' : '💾 Save'}
        </button>

        <div className="export-container">
          <button
            className="toolbar-btn"
            onClick={() => setShowExportMenu(!showExportMenu)}
            title="Export document"
          >
            📤 Export
          </button>
          
          {showExportMenu && (
            <div className="export-menu">
              <button
                className="export-option"
                onClick={() => handleExport('markdown')}
              >
                📄 Markdown
              </button>
              <button
                className="export-option"
                onClick={() => handleExport('html')}
              >
                🌐 HTML
              </button>
            </div>
          )}
        </div>

        <button
          className="toolbar-btn"
          onClick={() => window.location.reload()}
          title="Refresh"
        >
          🔄
        </button>
      </div>
    </div>
  );
};

export default DocumentToolbar;
