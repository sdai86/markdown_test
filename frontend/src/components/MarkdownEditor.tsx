import React, { useState, useCallback } from 'react';
import MDEditor from '@uiw/react-md-editor';
import '@uiw/react-md-editor/markdown-editor.css';
import '@uiw/react-markdown-preview/markdown.css';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  height?: number;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  value,
  onChange,
  onSave,
  onCancel,
  height = 200
}) => {
  const [localValue, setLocalValue] = useState(value);

  const handleChange = useCallback((val?: string) => {
    const newValue = val || '';
    setLocalValue(newValue);
    onChange(newValue);
  }, [onChange]);

  const handleSave = useCallback(() => {
    onSave();
  }, [onSave]);

  const handleCancel = useCallback(() => {
    setLocalValue(value); // Reset to original value
    onChange(value);
    onCancel();
  }, [value, onChange, onCancel]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCancel();
    } else if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    }
  }, [handleCancel, handleSave]);

  return (
    <div className="markdown-editor-container" onKeyDown={handleKeyDown}>
      <div className="markdown-editor-toolbar">
        <button 
          className="btn btn-primary btn-sm" 
          onClick={handleSave}
          title="Save (Ctrl+S)"
        >
          Save
        </button>
        <button 
          className="btn btn-secondary btn-sm" 
          onClick={handleCancel}
          title="Cancel (Esc)"
        >
          Cancel
        </button>
        <span className="editor-hint">
          Press Ctrl+S to save, Esc to cancel
        </span>
      </div>
      
      <MDEditor
        value={localValue}
        onChange={handleChange}
        height={height}
        preview="edit"
        hideToolbar={false}
        visibleDragbar={false}
        data-color-mode="light"
      />
    </div>
  );
};

export default MarkdownEditor;
