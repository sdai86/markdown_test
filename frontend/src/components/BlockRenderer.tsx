import React, { useState, useEffect } from 'react';
import { Block } from '../types';
import MarkdownRenderer from './MarkdownRenderer';
import MarkdownEditor from './MarkdownEditor';

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
  const [editContent, setEditContent] = useState(block.raw_content || block.content);

  // Update edit content when block changes
  useEffect(() => {
    setEditContent(block.raw_content || block.content);
  }, [block.content, block.raw_content]);

  const handleSave = () => {
    onSave(editContent);
  };

  const handleCancel = () => {
    setEditContent(block.raw_content || block.content);
    onCancel();
  };

  const handleContentChange = (content: string) => {
    setEditContent(content);
  };

  if (isEditing) {
    return (
      <div
        className={`block editing ${isActive ? 'active' : ''}`}
        data-block-id={block.id}
        data-order-index={block.order_index}
      >
        <MarkdownEditor
          value={editContent}
          onChange={handleContentChange}
          onSave={handleSave}
          onCancel={handleCancel}
          height={Math.max(150, editContent.split('\n').length * 20 + 100)}
        />
      </div>
    );
  }

  // For display, use the raw_content if available (original markdown), otherwise use content
  const displayContent = block.raw_content || block.content;

  return (
    <div
      className={`block ${isActive ? 'active' : ''}`}
      onClick={onEdit}
      data-block-id={block.id}
      data-order-index={block.order_index}
    >
      <MarkdownRenderer
        content={displayContent}
        className={`block-type-${block.type}`}
      />
    </div>
  );
};

export default BlockRenderer;
