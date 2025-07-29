# AST-Based Markdown Editor Design

## Overview
Redesign the markdown editor to use Abstract Syntax Tree (AST) for efficient handling of large documents (300+ pages) and scalable storage for millions of documents.

## Current Problems
1. **Storage Inefficiency**: 300+ database rows per document
2. **Limited Operations**: Can't handle structural changes (add/delete sections, reorder)
3. **Poor Scalability**: Millions of documents = billions of block records
4. **Complex State**: Managing hundreds of individual block states

## New Architecture

### 1. Database Schema
```sql
-- Single table for documents (replaces blocks table)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content_ast JSONB NOT NULL,        -- Complete document AST
    raw_markdown TEXT,                 -- Original markdown for export
    metadata JSONB DEFAULT '{}',       -- Document metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_documents_ast ON documents USING GIN (content_ast);
CREATE INDEX idx_documents_title ON documents (title);
CREATE INDEX idx_documents_updated ON documents (updated_at DESC);
```

### 2. AST Structure
```json
{
  "type": "document",
  "metadata": {
    "title": "Document Title",
    "wordCount": 15420,
    "pageCount": 312
  },
  "children": [
    {
      "id": "node_1",
      "type": "heading",
      "level": 1,
      "content": "Chapter 1: Introduction",
      "position": {"line": 1, "column": 1},
      "metadata": {"wordCount": 3}
    },
    {
      "id": "node_2",
      "type": "paragraph", 
      "content": "This chapter introduces the fundamental concepts...",
      "position": {"line": 3, "column": 1},
      "metadata": {"wordCount": 45}
    },
    {
      "id": "node_3",
      "type": "heading",
      "level": 2, 
      "content": "Section 1.1: Basic Principles",
      "position": {"line": 8, "column": 1},
      "children": [
        {
          "id": "node_4",
          "type": "paragraph",
          "content": "The basic principles include...",
          "metadata": {"wordCount": 120}
        },
        {
          "id": "node_5",
          "type": "list",
          "listType": "unordered",
          "children": [
            {
              "id": "node_6", 
              "type": "list_item",
              "content": "First principle: Clarity"
            }
          ]
        }
      ]
    }
  ]
}
```

### 3. Backend Architecture

#### Core Services
- **ASTService**: Parse markdown ↔ AST conversion
- **DocumentService**: CRUD operations on documents
- **NodeService**: AST node manipulation
- **ValidationService**: AST integrity validation

#### API Endpoints
```
GET    /documents                    # List documents
GET    /documents/{id}               # Get document with AST
PUT    /documents/{id}               # Update entire document
PATCH  /documents/{id}/nodes/{nodeId} # Update specific node
POST   /documents/{id}/nodes         # Insert new node
DELETE /documents/{id}/nodes/{nodeId} # Delete node
POST   /documents/{id}/export        # Export to various formats
```

### 4. Frontend Architecture

#### State Management
```typescript
interface DocumentState {
  id: string;
  title: string;
  ast: DocumentAST;
  virtualBlocks: VirtualBlock[];     // Flattened for virtualization
  editingNodeId: string | null;
  toc: TOCItem[];                    // Generated from AST
  metadata: DocumentMetadata;
}

interface VirtualBlock {
  id: string;
  type: NodeType;
  content: string;
  level?: number;
  astPath: number[];                 // Path to node in AST
  parentId?: string;
  depth: number;                     // Nesting level
  isCollapsible: boolean;            // For sections
  isCollapsed: boolean;
}
```

#### Key Components
- **DocumentProvider**: Manages document state and AST operations
- **VirtualizedEditor**: Renders flattened blocks with react-window
- **ASTNodeEditor**: Rich editor for individual nodes
- **DocumentOutline**: Hierarchical navigation from AST
- **OperationsToolbar**: Structural operations (add section, reorder, etc.)

### 5. Performance Optimizations

#### Large Document Handling (300+ pages)
1. **Lazy Loading**: Load AST progressively for very large documents
2. **Virtual Scrolling**: Render only visible blocks
3. **Debounced Saves**: Batch AST updates
4. **Memory Management**: Unload non-visible content from memory
5. **Chunked Processing**: Process large ASTs in chunks

#### Database Optimizations
1. **JSONB Indexing**: Efficient AST queries
2. **Compression**: Compress large AST documents
3. **Caching**: Redis cache for frequently accessed documents
4. **Connection Pooling**: Handle concurrent document access

### 6. Advanced Features

#### Structural Operations
- **Add Section**: Insert heading with auto-generated hierarchy
- **Delete Section**: Remove heading and all children
- **Promote/Demote**: Change heading levels
- **Reorder Sections**: Drag-and-drop with AST updates
- **Bulk Operations**: Move multiple nodes

#### Collaborative Features
- **Operational Transforms**: Conflict resolution for concurrent edits
- **Real-time Sync**: WebSocket updates for AST changes
- **Version History**: Store AST snapshots
- **Conflict Resolution**: Merge conflicting AST changes

#### Export Capabilities
- **Multiple Formats**: PDF, DOCX, HTML from AST
- **Custom Styling**: Apply themes during export
- **Partial Export**: Export specific sections
- **Batch Export**: Export multiple documents

### 7. Migration Strategy

#### Phase 1: Backend Foundation
1. Create new database schema
2. Implement AST parsing with markdown-it-py
3. Build AST manipulation services
4. Create new API endpoints

#### Phase 2: Frontend Redesign  
1. Implement AST state management
2. Create virtual block flattening
3. Update editor components
4. Add structural operations

#### Phase 3: Data Migration
1. Convert existing block data to AST
2. Migrate documents progressively
3. Validate AST integrity
4. Remove old blocks table

#### Phase 4: Advanced Features
1. Add collaborative editing
2. Implement export features
3. Performance optimizations
4. Analytics and monitoring

### 8. Technical Considerations

#### Memory Management
- **Large Documents**: Stream processing for 300+ page documents
- **AST Size Limits**: Implement size warnings and chunking
- **Browser Limits**: Monitor memory usage in frontend

#### Error Handling
- **AST Corruption**: Validation and recovery mechanisms
- **Partial Failures**: Graceful degradation for node operations
- **Backup Strategy**: Maintain raw markdown as fallback

#### Security
- **Input Validation**: Sanitize markdown content
- **AST Validation**: Prevent malicious AST structures
- **Access Control**: Document-level permissions

## Implementation Timeline
- **Week 1-2**: Backend AST foundation
- **Week 3-4**: Frontend state management
- **Week 5-6**: Editor components and operations
- **Week 7-8**: Migration and testing
- **Week 9-10**: Advanced features and optimization

## Success Metrics
- **Storage Efficiency**: 99% reduction in database rows
- **Performance**: <100ms load time for 300-page documents
- **Scalability**: Support millions of documents
- **User Experience**: Rich structural editing operations
