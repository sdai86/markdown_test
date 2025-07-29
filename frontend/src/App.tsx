import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { FixedSizeList as List } from 'react-window';
import TableOfContents from './components/TableOfContents';
import BlockRenderer from './components/BlockRenderer';
import Toolbar from './components/Toolbar';
import { Block, TOCItem, Document } from './types';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const App: React.FC = () => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [toc, setToc] = useState<TOCItem[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeBlockId, setActiveBlockId] = useState<string | null>(null);
  const [editingBlockId, setEditingBlockId] = useState<string | null>(null);
  const [visibleBlocks, setVisibleBlocks] = useState<Set<number>>(new Set());
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filteredBlocks, setFilteredBlocks] = useState<Block[]>([]);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  // Load blocks when document is selected
  useEffect(() => {
    if (selectedDocument) {
      loadBlocks();
      loadTOC();
    }
  }, [selectedDocument]);

  // Filter blocks based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredBlocks(blocks);
    } else {
      const filtered = blocks.filter(block =>
        block.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        block.raw_content?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredBlocks(filtered);
    }
  }, [blocks, searchTerm]);

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents`);
      setDocuments(response.data);
      if (response.data.length > 0 && !selectedDocument) {
        setSelectedDocument(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const loadBlocks = async () => {
    if (!selectedDocument) return;
    
    setLoading(true);
    const startTime = performance.now();
    
    try {
      const response = await axios.get(`${API_BASE_URL}/blocks`, {
        params: {
          document_id: selectedDocument,
          offset: 0,
          limit: 1000 // Load all blocks for now
        }
      });
      
      setBlocks(response.data.blocks);
      
      const loadTime = performance.now() - startTime;
      console.log(`Loaded ${response.data.blocks.length} blocks in ${loadTime.toFixed(2)}ms`);
      
    } catch (error) {
      console.error('Failed to load blocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTOC = async () => {
    if (!selectedDocument) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/toc`, {
        params: { document_id: selectedDocument }
      });
      setToc(response.data);
    } catch (error) {
      console.error('Failed to load TOC:', error);
    }
  };

  const updateBlock = useCallback(async (blockId: string, content: string) => {
    const startTime = performance.now();
    
    try {
      await axios.patch(`${API_BASE_URL}/blocks/${blockId}`, {
        content: content
      });
      
      // Update local state
      setBlocks(prev => prev.map(block => 
        block.id === blockId ? { ...block, content } : block
      ));
      
      const updateTime = performance.now() - startTime;
      console.log(`Updated block in ${updateTime.toFixed(2)}ms`);
      
    } catch (error) {
      console.error('Failed to update block:', error);
    }
  }, []);

  const scrollToBlock = useCallback((orderIndex: number) => {
    const blockElement = document.querySelector(`[data-order-index="${orderIndex}"]`);
    if (blockElement) {
      blockElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setActiveBlockId(blocks[orderIndex]?.id || null);
    }
  }, [blocks]);

  const handleTOCClick = useCallback((item: TOCItem) => {
    scrollToBlock(item.order_index);
  }, [scrollToBlock]);

  // Update active block based on visible blocks
  useEffect(() => {
    if (visibleBlocks.size > 0) {
      const firstVisibleIndex = Math.min(...visibleBlocks);
      const firstVisibleBlock = blocks[firstVisibleIndex];
      if (firstVisibleBlock) {
        setActiveBlockId(firstVisibleBlock.id);
      }
    }
  }, [visibleBlocks, blocks]);

  const handleItemsRendered = useCallback(({ visibleStartIndex, visibleStopIndex }: {
    visibleStartIndex: number;
    visibleStopIndex: number;
  }) => {
    const newVisibleBlocks = new Set<number>();
    for (let i = visibleStartIndex; i <= visibleStopIndex; i++) {
      newVisibleBlocks.add(i);
    }
    setVisibleBlocks(newVisibleBlocks);
  }, []);

  const exportMarkdown = async () => {
    if (!selectedDocument) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/export`, {
        params: { document_id: selectedDocument }
      });

      // Create and download file
      const blob = new Blob([response.data.markdown], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${documents.find(d => d.id === selectedDocument)?.title || 'document'}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      console.log(`Exported ${response.data.total_blocks} blocks in ${response.data.export_time_ms}ms`);
    } catch (error) {
      console.error('Failed to export markdown:', error);
    }
  };

  const renderBlock = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const displayBlocks = searchTerm ? filteredBlocks : blocks;
    const block = displayBlocks[index];
    if (!block) return null;

    return (
      <div style={style} data-order-index={block.order_index}>
        <BlockRenderer
          block={block}
          isEditing={editingBlockId === block.id}
          isActive={activeBlockId === block.id}
          onEdit={() => setEditingBlockId(block.id)}
          onSave={(content) => {
            updateBlock(block.id, content);
            setEditingBlockId(null);
          }}
          onCancel={() => setEditingBlockId(null)}
        />
      </div>
    );
  };

  return (
    <div className="app">
      <div className="sidebar">
        <h3>Table of Contents</h3>
        <TableOfContents
          items={toc}
          activeItemId={activeBlockId}
          onItemClick={handleTOCClick}
        />
      </div>
      
      <div className="main-content">
        <Toolbar
          documents={documents}
          selectedDocument={selectedDocument}
          onDocumentChange={setSelectedDocument}
          onRefresh={() => {
            loadBlocks();
            loadTOC();
          }}
          onExport={exportMarkdown}
        />

        <div className="search-bar">
          <input
            type="text"
            placeholder="Search blocks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <span className="search-results">
              {filteredBlocks.length} of {blocks.length} blocks
            </span>
          )}
        </div>
        
        <div className="editor-container">
          {loading ? (
            <div>Loading blocks...</div>
          ) : (searchTerm ? filteredBlocks : blocks).length > 0 ? (
            <List
              height={window.innerHeight - 180} // Adjust for toolbar and search
              itemCount={searchTerm ? filteredBlocks.length : blocks.length}
              itemSize={100} // Estimated item height
              width="100%"
              onItemsRendered={handleItemsRendered}
            >
              {renderBlock}
            </List>
          ) : searchTerm ? (
            <div>No blocks found matching "{searchTerm}". Try a different search term.</div>
          ) : (
            <div>No blocks found. Please select a document or upload markdown content.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
