/**
 * AST Block Renderer Component
 * Renders individual AST nodes as virtual blocks with rich editing
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import MDEditor from '@uiw/react-md-editor';
import { VirtualBlock } from '../services/documentService';
import 'highlight.js/styles/github.css';

interface ASTBlockRendererProps {
  block: VirtualBlock;
  isEditing: boolean;
  onEdit: (blockId: string) => void;
  onSave: (blockId: string, content: string) => void;
  onCancel: () => void;
  searchTerm?: string;
}

const ASTBlockRenderer: React.FC<ASTBlockRendererProps> = ({
  block,
  isEditing,
  onEdit,
  onSave,
  onCancel,
  searchTerm = '',
}) => {
  const [editContent, setEditContent] = useState(block.content);
  const [isHovered, setIsHovered] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);

  // Update edit content when block content changes
  useEffect(() => {
    if (!isEditing) {
      setEditContent(block.content);
    }
  }, [block.content, isEditing]);

  // Handle save
  const handleSave = useCallback(() => {
    onSave(block.id, editContent);
  }, [block.id, editContent, onSave]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    setEditContent(block.content);
    onCancel();
  }, [block.content, onCancel]);

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCancel();
    } else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
  }, [handleCancel, handleSave]);

  // Highlight search terms
  const highlightSearchTerm = useCallback((text: string) => {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }, [searchTerm]);

  // Get block type icon
  const getBlockIcon = () => {
    switch (block.type) {
      case 'heading':
        return `H${block.level || 1}`;
      case 'paragraph':
        return '¶';
      case 'list':
        return block.listType === 'ordered' ? '#' : '•';
      case 'code_block':
        return '</>';
      case 'blockquote':
        return '"';
      case 'horizontal_rule':
        return '—';
      default:
        return '◦';
    }
  };

  // Get block type class
  const getBlockTypeClass = () => {
    const baseClass = 'ast-block';
    const typeClass = `ast-block-${block.type}`;
    const levelClass = block.level ? `ast-block-level-${block.level}` : '';
    const depthClass = `ast-block-depth-${block.depth}`;
    const editingClass = isEditing ? 'editing' : '';
    const hoveredClass = isHovered ? 'hovered' : '';
    
    return [baseClass, typeClass, levelClass, depthClass, editingClass, hoveredClass]
      .filter(Boolean)
      .join(' ');
  };

  // Render content based on block type
  const renderContent = () => {
    if (isEditing) {
      return (
        <div className="ast-block-editor" ref={editorRef}>
          <MDEditor
            value={editContent}
            onChange={(value) => setEditContent(value || '')}
            onKeyDown={handleKeyDown}
            preview="edit"
            hideToolbar={false}
            height={300}
            data-color-mode="light"
          />
          <div className="editor-actions">
            <button 
              className="save-btn" 
              onClick={handleSave}
              title="Save (Ctrl+S)"
            >
              Save
            </button>
            <button 
              className="cancel-btn" 
              onClick={handleCancel}
              title="Cancel (Esc)"
            >
              Cancel
            </button>
          </div>
        </div>
      );
    }

    // Render different content types
    switch (block.type) {
      case 'heading':
        const HeadingTag = `h${Math.min(block.level || 1, 6)}` as keyof JSX.IntrinsicElements;
        return (
          <HeadingTag 
            className="ast-heading"
            dangerouslySetInnerHTML={{ 
              __html: highlightSearchTerm(block.content) 
            }}
          />
        );

      case 'code_block':
        return (
          <div className="ast-code-block">
            {block.language && (
              <div className="code-language">{block.language}</div>
            )}
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight, rehypeRaw]}
            >
              {`\`\`\`${block.language || ''}\n${block.content}\n\`\`\``}
            </ReactMarkdown>
          </div>
        );

      case 'list':
        const ListTag = block.listType === 'ordered' ? 'ol' : 'ul';
        return (
          <ListTag className="ast-list">
            <li dangerouslySetInnerHTML={{ 
              __html: highlightSearchTerm(block.content) 
            }} />
          </ListTag>
        );

      case 'blockquote':
        return (
          <blockquote 
            className="ast-blockquote"
            dangerouslySetInnerHTML={{ 
              __html: highlightSearchTerm(block.content) 
            }}
          />
        );

      case 'horizontal_rule':
        return <hr className="ast-hr" />;

      case 'paragraph':
      default:
        return (
          <div className="ast-paragraph">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
            >
              {highlightSearchTerm(block.content)}
            </ReactMarkdown>
          </div>
        );
    }
  };

  return (
    <div 
      className={getBlockTypeClass()}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      data-block-id={block.id}
      data-block-type={block.type}
    >
      {/* Block header with metadata */}
      <div className="ast-block-header">
        <div className="block-info">
          <span className="block-icon" title={`${block.type} (level ${block.level || 0})`}>
            {getBlockIcon()}
          </span>
          <span className="block-path">
            {block.astPath.join('.')}
          </span>
          {block.position && (
            <span className="block-position">
              L{block.position.line}
            </span>
          )}
        </div>
        
        {!isEditing && isHovered && (
          <div className="block-actions">
            <button 
              className="edit-btn"
              onClick={() => onEdit(block.id)}
              title="Edit block"
            >
              ✏️
            </button>
            {block.isCollapsible && (
              <button 
                className="collapse-btn"
                title={block.isCollapsed ? "Expand" : "Collapse"}
              >
                {block.isCollapsed ? '▶' : '▼'}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Block content */}
      <div className="ast-block-content">
        {renderContent()}
      </div>

      {/* Block footer with additional info */}
      {!isEditing && (
        <div className="ast-block-footer">
          <div className="block-stats">
            <span className="word-count">
              {block.content.split(/\s+/).filter(Boolean).length} words
            </span>
            {block.depth > 0 && (
              <span className="depth-indicator">
                {'  '.repeat(block.depth)}└─
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ASTBlockRenderer;
