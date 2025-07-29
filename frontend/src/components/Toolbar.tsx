import React from 'react';
import { Document } from '../types';

interface ToolbarProps {
  documents: Document[];
  selectedDocument: string | null;
  onDocumentChange: (documentId: string) => void;
  onRefresh: () => void;
}

const Toolbar: React.FC<ToolbarProps> = ({
  documents,
  selectedDocument,
  onDocumentChange,
  onRefresh
}) => {
  return (
    <div className="toolbar">
      <div className="toolbar-section">
        <label htmlFor="document-select">Document:</label>
        <select
          id="document-select"
          value={selectedDocument || ''}
          onChange={(e) => onDocumentChange(e.target.value)}
        >
          <option value="">Select a document</option>
          {documents.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.title} ({doc.total_blocks} blocks)
            </option>
          ))}
        </select>
      </div>
      
      <div className="toolbar-section">
        <button onClick={onRefresh} className="btn btn-secondary">
          Refresh
        </button>
      </div>
      
      <div className="toolbar-section">
        <span className="status">
          {selectedDocument ? 
            `${documents.find(d => d.id === selectedDocument)?.total_blocks || 0} blocks loaded` : 
            'No document selected'
          }
        </span>
      </div>
    </div>
  );
};

export default Toolbar;
