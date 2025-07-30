import React, { useState, useEffect, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { documentService } from '../services/documentService';

// Add CSS styles
const styles = `
  .document-viewer {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  }

  .toc-item {
    margin: 5px 0;
  }

  .toc-item.level-1 {
    font-weight: bold;
    margin-top: 15px;
  }

  .toc-item.level-2 {
    margin-left: 20px;
    font-weight: 600;
  }

  .toc-item.level-3 {
    margin-left: 40px;
  }

  .toc-item.level-4 {
    margin-left: 60px;
  }

  .toc-link {
    color: #007acc;
    text-decoration: none;
    display: block;
    padding: 3px 0;
    border-radius: 3px;
  }

  .toc-link:hover {
    background-color: #e3f2fd;
    text-decoration: underline;
  }

  .editable-section {
    transition: all 0.2s ease;
    padding: 5px;
    margin: 10px 0;
    border-radius: 4px;
  }

  .editable-section:hover {
    background-color: #f5f5f5 !important;
    border-left: 4px solid #007acc !important;
  }

  .content h1, .content h2, .content h3 {
    position: relative;
  }

  .content h1::after, .content h2::after, .content h3::after {
    content: "✏️ Click to edit";
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 12px;
    color: #666;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .content h1:hover::after, .content h2:hover::after, .content h3:hover::after {
    opacity: 1;
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = styles;
  document.head.appendChild(styleElement);
}

interface DocumentViewerProps {
  documentId: string;
}

interface TocItem {
  id: string;
  text: string;
  level: number;
  children: TocItem[];
}

interface Section {
  id: string;
  title: string;
  level: number;
  startIndex: number;
  endIndex: number;
  content: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documentId }) => {
  const [markdownContent, setMarkdownContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingSection, setEditingSection] = useState<Section | null>(null);
  const [editContent, setEditContent] = useState<string>('');
  const [showToc, setShowToc] = useState(true);

  useEffect(() => {
    loadDocument();
  }, [documentId]);

  const loadDocument = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get the full markdown content via export API
      const content = await documentService.exportDocument(documentId);
      setMarkdownContent(content);

    } catch (err) {
      console.error('Error loading document:', err);
      setError('Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  // Parse table of contents from markdown
  const tableOfContents = useMemo(() => {
    const lines = markdownContent.split('\n');
    const toc: TocItem[] = [];
    const stack: TocItem[] = [];

    lines.forEach((line: string, index: number) => {
      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        const level = match[1].length;
        const text = match[2];
        const id = `heading-${index}`;

        const item: TocItem = {
          id,
          text,
          level,
          children: []
        };

        // Find the correct parent
        while (stack.length > 0 && stack[stack.length - 1].level >= level) {
          stack.pop();
        }

        if (stack.length === 0) {
          toc.push(item);
        } else {
          stack[stack.length - 1].children.push(item);
        }

        stack.push(item);
      }
    });

    return toc;
  }, [markdownContent]);

  // Parse sections for editing
  const sections = useMemo(() => {
    const lines = markdownContent.split('\n');
    const sectionList: Section[] = [];
    let currentSection: Section | null = null;

    lines.forEach((line: string, index: number) => {
      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        // Close previous section
        if (currentSection) {
          currentSection.endIndex = index - 1;
          currentSection.content = lines.slice(currentSection.startIndex, index).join('\n');
          sectionList.push(currentSection);
        }

        // Start new section
        const level = match[1].length;
        const title = match[2];
        const id = `section-${index}`;

        currentSection = {
          id,
          title,
          level,
          startIndex: index,
          endIndex: lines.length - 1,
          content: ''
        };
      }
    });

    // Close last section
    if (currentSection) {
      (currentSection as Section).content = lines.slice((currentSection as Section).startIndex).join('\n');
      sectionList.push(currentSection as Section);
    }

    return sectionList;
  }, [markdownContent]);

  const handleExport = async () => {
    try {
      const content = await documentService.exportDocument(documentId);
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document-${documentId}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting document:', err);
      setError('Failed to export document');
    }
  };

  const handleSectionClick = (section: Section) => {
    setEditingSection(section);
    setEditContent(section.content);
  };

  const handleSaveEdit = async () => {
    if (!editingSection) return;

    try {
      // Replace the section content in the full document
      const lines = markdownContent.split('\n');
      const newLines = [
        ...lines.slice(0, editingSection.startIndex),
        ...editContent.split('\n'),
        ...lines.slice(editingSection.endIndex + 1)
      ];
      const newContent = newLines.join('\n');

      // Update the document via API
      await documentService.updateDocumentFromMarkdown(documentId, newContent);

      // Reload the document
      await loadDocument();
      setEditingSection(null);
      setEditContent('');
    } catch (err) {
      console.error('Error saving section:', err);
      setError('Failed to save section');
    }
  };

  const handleCancelEdit = () => {
    setEditingSection(null);
    setEditContent('');
  };

  const renderTocItem = (item: TocItem): any => {
    return React.createElement('div', { key: item.id, className: `toc-item level-${item.level}` },
      React.createElement('a', {
        href: `#${item.id}`,
        className: 'toc-link',
        onClick: (e: any) => {
          e.preventDefault();
          const element = document.getElementById(item.id);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
          }
        }
      }, item.text),
      item.children.length > 0 && React.createElement('div', { className: 'toc-children' },
        item.children.map((child: TocItem) => renderTocItem(child))
      )
    );
  };

  const customComponents = {
    h1: ({ children, ...props }: any) => {
      const section = sections.find((s: Section) => s.title === children);
      return React.createElement('h1', {
        ...props,
        id: section?.id,
        className: 'editable-section',
        onClick: () => section && handleSectionClick(section),
        style: { cursor: 'pointer', borderLeft: '4px solid transparent' },
        onMouseEnter: (e: any) => {
          e.target.style.borderLeft = '4px solid #007acc';
          e.target.style.backgroundColor = '#f5f5f5';
        },
        onMouseLeave: (e: any) => {
          e.target.style.borderLeft = '4px solid transparent';
          e.target.style.backgroundColor = 'transparent';
        }
      }, children);
    },
    h2: ({ children, ...props }: any) => {
      const section = sections.find((s: Section) => s.title === children);
      return React.createElement('h2', {
        ...props,
        id: section?.id,
        className: 'editable-section',
        onClick: () => section && handleSectionClick(section),
        style: { cursor: 'pointer', borderLeft: '4px solid transparent' },
        onMouseEnter: (e: any) => {
          e.target.style.borderLeft = '4px solid #007acc';
          e.target.style.backgroundColor = '#f5f5f5';
        },
        onMouseLeave: (e: any) => {
          e.target.style.borderLeft = '4px solid transparent';
          e.target.style.backgroundColor = 'transparent';
        }
      }, children);
    },
    h3: ({ children, ...props }: any) => {
      const section = sections.find((s: Section) => s.title === children);
      return React.createElement('h3', {
        ...props,
        id: section?.id,
        className: 'editable-section',
        onClick: () => section && handleSectionClick(section),
        style: { cursor: 'pointer', borderLeft: '4px solid transparent' },
        onMouseEnter: (e: any) => {
          e.target.style.borderLeft = '4px solid #007acc';
          e.target.style.backgroundColor = '#f5f5f5';
        },
        onMouseLeave: (e: any) => {
          e.target.style.borderLeft = '4px solid transparent';
          e.target.style.backgroundColor = 'transparent';
        }
      }, children);
    }
  };

  if (loading) {
    return React.createElement('div', { className: 'loading' }, 'Loading document...');
  }

  if (error) {
    return React.createElement('div', { className: 'error' }, `Error: ${error}`);
  }

  return React.createElement('div', { className: 'document-viewer', style: { display: 'flex', height: '100vh' } },
    // Sidebar with ToC
    showToc && React.createElement('div', {
      className: 'sidebar',
      style: {
        width: '300px',
        borderRight: '1px solid #ddd',
        padding: '20px',
        overflowY: 'auto',
        backgroundColor: '#f9f9f9'
      }
    },
      React.createElement('div', { className: 'sidebar-header' },
        React.createElement('h3', { style: { margin: '0 0 20px 0' } }, 'Table of Contents'),
        React.createElement('button', {
          onClick: () => setShowToc(false),
          style: { float: 'right', background: 'none', border: 'none', cursor: 'pointer' }
        }, '✕')
      ),
      React.createElement('div', { className: 'toc' },
        tableOfContents.map(item => renderTocItem(item))
      )
    ),

    // Main content area
    React.createElement('div', {
      className: 'main-area',
      style: { flex: 1, display: 'flex', flexDirection: 'column' }
    },
      // Toolbar
      React.createElement('div', {
        className: 'toolbar',
        style: {
          padding: '10px 20px',
          borderBottom: '1px solid #ddd',
          backgroundColor: '#fff',
          display: 'flex',
          gap: '10px',
          alignItems: 'center'
        }
      },
        !showToc && React.createElement('button', {
          onClick: () => setShowToc(true),
          style: { padding: '5px 10px' }
        }, '📋 Show ToC'),
        React.createElement('button', {
          onClick: handleExport,
          style: { padding: '5px 10px' }
        }, '📤 Export'),
        React.createElement('button', {
          onClick: loadDocument,
          style: { padding: '5px 10px' }
        }, '🔄 Refresh'),
        React.createElement('span', { style: { marginLeft: 'auto', fontSize: '14px', color: '#666' } },
          `${sections.length} sections • Click any heading to edit`)
      ),

      // Content area
      React.createElement('div', {
        className: 'content',
        style: {
          flex: 1,
          padding: '20px',
          overflowY: 'auto',
          backgroundColor: '#fff'
        }
      },
        React.createElement(ReactMarkdown, {
          remarkPlugins: [remarkGfm],
          components: customComponents,
          children: markdownContent
        })
      )
    ),

    // Edit modal
    editingSection && React.createElement('div', {
      className: 'edit-modal',
      style: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }
    },
      React.createElement('div', {
        className: 'edit-modal-content',
        style: {
          backgroundColor: '#fff',
          padding: '20px',
          borderRadius: '8px',
          width: '80%',
          height: '80%',
          display: 'flex',
          flexDirection: 'column'
        }
      },
        React.createElement('div', { className: 'edit-header', style: { marginBottom: '20px' } },
          React.createElement('h3', { style: { margin: 0 } }, `Edit Section: ${editingSection.title}`),
          React.createElement('p', { style: { margin: '5px 0', color: '#666' } },
            'Edit the raw markdown content for this section. You can add, modify, or delete subsections.')
        ),
        React.createElement('textarea', {
          value: editContent,
          onChange: (e: any) => setEditContent(e.target.value),
          style: {
            flex: 1,
            width: '100%',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '14px',
            resize: 'none'
          },
          placeholder: 'Enter markdown content...'
        }),
        React.createElement('div', {
          className: 'edit-actions',
          style: { marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'flex-end' }
        },
          React.createElement('button', {
            onClick: handleCancelEdit,
            style: { padding: '10px 20px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer' }
          }, 'Cancel'),
          React.createElement('button', {
            onClick: handleSaveEdit,
            style: {
              padding: '10px 20px',
              backgroundColor: '#007acc',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }
          }, 'Save Changes')
        )
      )
    )
  );
};

export default DocumentViewer;