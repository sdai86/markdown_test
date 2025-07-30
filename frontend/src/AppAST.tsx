/**
 * AST-based Markdown Editor App
 * Main application component using document-based rendering
 */

import React from 'react';
import DocumentViewer from './components/DocumentViewer';

const SAMPLE_DOCUMENT_ID = '550e8400-e29b-41d4-a716-446655440001'; // Large 945-page document

// Main App component
const App: React.FC = () => {
  return (
    <div className="App">
      <DocumentViewer documentId={SAMPLE_DOCUMENT_ID} />
    </div>
  );
};

export default App;
