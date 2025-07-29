import React, { useState, useEffect, useRef } from 'react';
import debounce from 'lodash.debounce';
import { Block } from '../types';

interface BlockRendererProps {
  block: Block;
  isEditing: boolean;
  isActive: boolean;
  onEdit: () => void;
  onSave: (content: string) => void;
  onCancel: () => void;
}

const BlockRenderer: React.FC<BlockRendererProps> = ({
  block,
  isEditing,
  isActive,
  onEdit,
  onSave,
  onCancel
}) => {
  const [editContent, setEditContent] = useState(block.content);
  const editRef = useRef<HTMLDivElement>(null);

  // Update edit content when block changes
  useEffect(() => {
    setEditContent(block.content);
  }, [block.content]);

  // Focus on edit element when editing starts
  useEffect(() => {
    if (isEditing && editRef.current) {
      editRef.current.focus();
      // Place cursor at end
      const range = document.createRange();
      const selection = window.getSelection();
      range.selectNodeContents(editRef.current);
      range.collapse(false);
      selection?.removeAllRanges();
      selection?.addRange(range);
    }
  }, [isEditing]);

  // Debounced save function
  const debouncedSave = debounce((content: string) => {
    if (content !== block.content) {
      onSave(content);
    }
  }, 500);

  const handleContentChange = (content: string) => {
    setEditContent(content);
    debouncedSave(content);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      onSave(editContent);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setEditContent(block.content);
      onCancel();
    }
  };

  const renderEditableContent = () => {
    switch (block.type) {
      case 'code':
        return (
          <textarea
            ref={editRef as any}
            className="block-code-editor"
            value={editContent}
            onChange={(e) => handleContentChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => onSave(editContent)}
            rows={editContent.split('\n').length + 1}
          />
        );

      default:
        return (
          <div
            ref={editRef}
            className="block-content"
            contentEditable
            suppressContentEditableWarning
            onInput={(e) => handleContentChange(e.currentTarget.textContent || '')}
            onKeyDown={handleKeyDown}
            onBlur={() => onSave(editContent)}
          >
            {editContent}
          </div>
        );
    }
  };

  const renderContent = () => {
    if (isEditing) {
      return renderEditableContent();
    }

    switch (block.type) {
      case 'heading':
        const HeadingTag = `h${Math.min(block.level, 6)}` as keyof JSX.IntrinsicElements;
        return (
          <HeadingTag className={`block-heading level-${block.level}`}>
            {block.content}
          </HeadingTag>
        );

      case 'code':
        return (
          <pre className="block-code">
            <code>{block.content}</code>
          </pre>
        );

      case 'blockquote':
        return (
          <blockquote className="block-blockquote">
            {block.content}
          </blockquote>
        );

      case 'list_item':
        const indent = '  '.repeat(block.level);
        const marker = block.metadata?.list_type === 'ordered' ? '1.' : '•';
        return (
          <div className="block-list-item">
            {indent}{marker} {block.content}
          </div>
        );

      case 'paragraph':
      default:
        return (
          <p className="block-paragraph">
            {block.content}
          </p>
        );
    }
  };

  return (
    <div
      className={`block ${isEditing ? 'editing' : ''} ${isActive ? 'active' : ''}`}
      onClick={!isEditing ? onEdit : undefined}
      data-block-id={block.id}
      data-order-index={block.order_index}
    >
      {renderContent()}
      {isEditing && (
        <div className="block-edit-hint">
          <small>Ctrl+Enter to save, Escape to cancel</small>
        </div>
      )}
    </div>
  );
};

export default BlockRenderer;
