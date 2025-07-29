/**
 * AST-based Markdown Editor App
 * Main application component using AST document management
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { VariableSizeList as List } from 'react-window';
import debounce from 'lodash.debounce';
import './App.css';
import { DocumentProvider, useDocument } from './contexts/DocumentContext';
import { VirtualBlock } from './services/documentService';
import ASTBlockRenderer from './components/ASTBlockRenderer';
import DocumentOutline from './components/DocumentOutline';
import DocumentToolbar from './components/DocumentToolbar';
import RawMarkdownEditor from './components/RawMarkdownEditor';

const SAMPLE_DOCUMENT_ID = '550e8400-e29b-41d4-a716-446655440001'; // Large 945-page document

const DocumentEditor: React.FC = () => {
  const { 
    state, 
    loadDocument, 
    updateNodeContent, 
    setEditingNode, 
    setSearchTerm,
    saveDocument 
  } = useDocument();

  const [showOutline, setShowOutline] = useState(true);
  const [showRawEditor, setShowRawEditor] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState<{
    loadTime: number;
    renderTime: number;
    blockCount: number;
  } | null>(null);

  const listRef = useRef<any>(null);

  // Load document on mount
  useEffect(() => {
    const startTime = performance.now();
    
    loadDocument(SAMPLE_DOCUMENT_ID).then(() => {
      const loadTime = performance.now() - startTime;
      setPerformanceMetrics({
        loadTime,
        renderTime: 0,
        blockCount: state.virtualBlocks.length,
      });
    });
  }, [loadDocument]);

  // Reset list cache when editing state changes
  useEffect(() => {
    if (listRef.current) {
      listRef.current.resetAfterIndex(0);
    }
  }, [state.editingNodeId]);

  // Handle search
  const handleSearch = useCallback((term: string) => {
    setSearchTerm(term);
  }, [setSearchTerm]);

  // Handle node content updates with debouncing
  const debouncedUpdateContent = useCallback(
    debounce((nodeId: string, content: string) => {
      updateNodeContent(nodeId, content);
    }, 500),
    [updateNodeContent]
  );

  // Handle block editing
  const handleEditBlock = useCallback((blockId: string) => {
    setEditingNode(blockId);
  }, [setEditingNode]);

  const handleSaveBlock = useCallback((blockId: string, content: string) => {
    debouncedUpdateContent(blockId, content);
    setEditingNode(null);
  }, [debouncedUpdateContent, setEditingNode]);

  const handleCancelEdit = useCallback(() => {
    setEditingNode(null);
  }, [setEditingNode]);

  // Handle outline navigation
  const handleOutlineClick = useCallback((nodeId: string) => {
    const currentBlocks = state.searchTerm ? state.filteredBlocks : state.virtualBlocks;
    const blockIndex = currentBlocks.findIndex(block => block.id === nodeId);
    
    if (blockIndex !== -1 && listRef.current) {
      listRef.current.scrollToItem(blockIndex, 'start');
    }
  }, [state.searchTerm, state.filteredBlocks, state.virtualBlocks]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 's':
            e.preventDefault();
            saveDocument();
            break;
          case 'f':
            e.preventDefault();
            // Focus search input
            const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement;
            if (searchInput) {
              searchInput.focus();
            }
            break;
        }
      }
      
      if (e.key === 'Escape' && state.editingNodeId) {
        handleCancelEdit();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [saveDocument, state.editingNodeId, handleCancelEdit]);

  // Calculate item size for virtualized list
  const getItemSize = useCallback((index: number) => {
    const currentBlocks = state.searchTerm ? state.filteredBlocks : state.virtualBlocks;
    const block = currentBlocks[index];
    
    if (!block) return 150;
    
    // Use larger size for editing blocks to prevent overlap
    if (state.editingNodeId === block.id) {
      return 400; // Increased for rich editor
    }
    
    // Dynamic sizing based on content type
    switch (block.type) {
      case 'heading':
        return 80 + (block.level ? (6 - block.level) * 10 : 0);
      case 'code_block':
        const lines = block.content.split('\n').length;
        return Math.max(120, lines * 20 + 60);
      case 'list':
        return 60;
      case 'paragraph':
        const words = block.content.split(' ').length;
        return Math.max(80, Math.min(200, words * 2 + 60));
      default:
        return 100;
    }
  }, [state.searchTerm, state.filteredBlocks, state.virtualBlocks, state.editingNodeId]);

  // Render virtual block item
  const renderBlockItem = useCallback(({ index, style }: { index: number; style: React.CSSProperties }) => {
    const currentBlocks = state.searchTerm ? state.filteredBlocks : state.virtualBlocks;
    const block = currentBlocks[index];
    
    if (!block) return null;

    const renderStartTime = performance.now();
    
    const component = (
      <div style={style}>
        <ASTBlockRenderer
          block={block}
          isEditing={state.editingNodeId === block.id}
          onEdit={handleEditBlock}
          onSave={handleSaveBlock}
          onCancel={handleCancelEdit}
          searchTerm={state.searchTerm}
        />
      </div>
    );

    // Track render performance for first few blocks
    if (index < 10) {
      const renderTime = performance.now() - renderStartTime;
      setPerformanceMetrics(prev => prev ? ({
        ...prev,
        renderTime: Math.max(prev.renderTime || 0, renderTime),
      }) : {
        loadTime: 0,
        renderTime,
        blockCount: 0,
      });
    }

    return component;
  }, [
    state.searchTerm, 
    state.filteredBlocks, 
    state.virtualBlocks, 
    state.editingNodeId,
    handleEditBlock,
    handleSaveBlock,
    handleCancelEdit
  ]);

  const currentBlocks = state.searchTerm ? state.filteredBlocks : state.virtualBlocks;

  if (state.loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading AST-based document...</p>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="app">
        <div className="error-container">
          <h2>Error</h2>
          <p>{state.error}</p>
          <button onClick={() => window.location.reload()}>Reload</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <DocumentToolbar
        document={state.document}
        onSearch={handleSearch}
        onSave={saveDocument}
        onToggleOutline={() => setShowOutline(!showOutline)}
        onRawEdit={() => setShowRawEditor(true)}
        showOutline={showOutline}
        isDirty={state.isDirty}
        lastSaved={state.lastSaved}
      />

      <div className="app-content">
        {showOutline && (
          <DocumentOutline
            outline={state.outline}
            onItemClick={handleOutlineClick}
            currentNodeId={state.editingNodeId}
          />
        )}

        <div className="editor-container">
          {state.document && (
            <div className="document-header">
              <h1>{state.document.title}</h1>
              <div className="document-stats">
                <span>{state.document.metadata.wordCount} words</span>
                <span>{state.document.metadata.pageCount} pages</span>
                <span>{currentBlocks.length} blocks</span>
                {state.searchTerm && (
                  <span className="search-results">
                    {state.filteredBlocks.length} matches
                  </span>
                )}
              </div>
            </div>
          )}

          {currentBlocks.length > 0 ? (
            <List
              ref={listRef}
              height={window.innerHeight - 200}
              itemCount={currentBlocks.length}
              itemSize={getItemSize}
              width="100%"
              className="virtual-list"
            >
              {renderBlockItem}
            </List>
          ) : (
            <div className="empty-state">
              {state.searchTerm ? (
                <p>No blocks match your search term "{state.searchTerm}"</p>
              ) : (
                <p>No content available</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Performance metrics */}
      {performanceMetrics && (
        <div className="performance-metrics">
          <small>
            Load: {performanceMetrics.loadTime?.toFixed(1) || '0.0'}ms |
            Render: {performanceMetrics.renderTime?.toFixed(1) || '0.0'}ms |
            Blocks: {performanceMetrics.blockCount || 0}
          </small>
        </div>
      )}

      {/* Raw Markdown Editor */}
      {showRawEditor && (
        <RawMarkdownEditor onClose={() => setShowRawEditor(false)} />
      )}
    </div>
  );
};

// Main App component with DocumentProvider
const App: React.FC = () => {
  return (
    <DocumentProvider>
      <DocumentEditor />
    </DocumentProvider>
  );
};

export default App;
