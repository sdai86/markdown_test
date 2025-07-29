import React, { useState, useCallback, useEffect } from 'react';
import { useDocument } from '../contexts/DocumentContext';

interface RawMarkdownEditorProps {
  onClose: () => void;
}

const RawMarkdownEditor: React.FC<RawMarkdownEditorProps> = ({ onClose }) => {
  const { state, updateDocumentFromMarkdown } = useDocument();
  const [rawMarkdown, setRawMarkdown] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize with current document's raw markdown
  useEffect(() => {
    if (state.document?.raw_markdown) {
      setRawMarkdown(state.document.raw_markdown);
    }
  }, [state.document?.raw_markdown]);

  const handleMarkdownChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = event.target.value;
    setRawMarkdown(newValue);
    setHasChanges(newValue !== state.document?.raw_markdown);
  }, [state.document?.raw_markdown]);

  const handleSave = useCallback(async () => {
    if (!hasChanges || !state.document) return;

    setIsLoading(true);
    try {
      await updateDocumentFromMarkdown(state.document.id, rawMarkdown);
      setHasChanges(false);
      // Don't close automatically - let user decide when to close
    } catch (error) {
      console.error('Failed to update document from markdown:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [hasChanges, state.document, rawMarkdown, updateDocumentFromMarkdown]);

  const handleCancel = useCallback(() => {
    if (hasChanges) {
      const confirmed = window.confirm('You have unsaved changes. Are you sure you want to close without saving?');
      if (!confirmed) return;
    }
    onClose();
  }, [hasChanges, onClose]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.ctrlKey || event.metaKey) {
      if (event.key === 's') {
        event.preventDefault();
        handleSave();
      } else if (event.key === 'Escape') {
        event.preventDefault();
        handleCancel();
      }
    }
  }, [handleSave, handleCancel]);

  return (
    <div className="raw-markdown-editor-overlay">
      <div className="raw-markdown-editor">
        <div className="raw-markdown-editor-header">
          <h2>Raw Markdown Editor</h2>
          <div className="raw-markdown-editor-actions">
            <span className="document-info">
              {state.document?.title} - {state.document?.metadata?.wordCount || 0} words
            </span>
            {hasChanges && <span className="changes-indicator">●</span>}
            <button
              onClick={handleSave}
              disabled={!hasChanges || isLoading}
              className="save-button"
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
            <button onClick={handleCancel} className="cancel-button">
              Close
            </button>
          </div>
        </div>

        <div className="raw-markdown-editor-content">
          <textarea
            value={rawMarkdown}
            onChange={handleMarkdownChange}
            onKeyDown={handleKeyDown}
            placeholder="Enter your markdown content here..."
            className="raw-markdown-textarea"
            autoFocus
          />
        </div>

        <div className="raw-markdown-editor-footer">
          <div className="editor-help">
            <strong>Keyboard shortcuts:</strong>
            <span>Ctrl/Cmd + S to save</span>
            <span>Esc to close</span>
          </div>
          <div className="editor-stats">
            Characters: {rawMarkdown.length} | 
            Lines: {rawMarkdown.split('\n').length} |
            Words: {rawMarkdown.split(/\s+/).filter(word => word.length > 0).length}
          </div>
        </div>
      </div>

      <style jsx>{`
        .raw-markdown-editor-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .raw-markdown-editor {
          background: white;
          border-radius: 8px;
          width: 90vw;
          height: 90vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .raw-markdown-editor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid #e0e0e0;
          background: #f8f9fa;
          border-radius: 8px 8px 0 0;
        }

        .raw-markdown-editor-header h2 {
          margin: 0;
          font-size: 18px;
          color: #333;
        }

        .raw-markdown-editor-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .document-info {
          font-size: 14px;
          color: #666;
        }

        .changes-indicator {
          color: #ff6b35;
          font-size: 20px;
          line-height: 1;
        }

        .save-button {
          background: #007bff;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .save-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .save-button:not(:disabled):hover {
          background: #0056b3;
        }

        .cancel-button {
          background: #6c757d;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .cancel-button:hover {
          background: #545b62;
        }

        .raw-markdown-editor-content {
          flex: 1;
          padding: 0;
          overflow: hidden;
        }

        .raw-markdown-textarea {
          width: 100%;
          height: 100%;
          border: none;
          outline: none;
          padding: 20px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 14px;
          line-height: 1.5;
          resize: none;
          background: #fafafa;
        }

        .raw-markdown-editor-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 20px;
          border-top: 1px solid #e0e0e0;
          background: #f8f9fa;
          border-radius: 0 0 8px 8px;
          font-size: 12px;
          color: #666;
        }

        .editor-help {
          display: flex;
          gap: 16px;
          align-items: center;
        }

        .editor-help strong {
          margin-right: 8px;
        }

        .editor-stats {
          font-family: monospace;
        }
      `}</style>
    </div>
  );
};

export default RawMarkdownEditor;
