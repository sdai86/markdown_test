/**
 * AST-based Document Context
 * Provides document state management with AST operations
 */

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { 
  Document, 
  DocumentAST, 
  VirtualBlock, 
  OutlineItem, 
  NodeOperation,
  documentService 
} from '../services/documentService';
import { debounce } from 'lodash';

interface DocumentState {
  document: Document | null;
  virtualBlocks: VirtualBlock[];
  outline: OutlineItem[];
  editingNodeId: string | null;
  searchTerm: string;
  filteredBlocks: VirtualBlock[];
  loading: boolean;
  error: string | null;
  lastSaved: Date | null;
  isDirty: boolean;
}

type DocumentAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_DOCUMENT'; payload: { document: Document; blocks: VirtualBlock[]; outline: OutlineItem[] } }
  | { type: 'UPDATE_AST'; payload: DocumentAST }
  | { type: 'SET_EDITING_NODE'; payload: string | null }
  | { type: 'SET_SEARCH_TERM'; payload: string }
  | { type: 'UPDATE_NODE_CONTENT'; payload: { nodeId: string; content: string } }
  | { type: 'SET_LAST_SAVED'; payload: Date }
  | { type: 'SET_DIRTY'; payload: boolean };

const initialState: DocumentState = {
  document: null,
  virtualBlocks: [],
  outline: [],
  editingNodeId: null,
  searchTerm: '',
  filteredBlocks: [],
  loading: false,
  error: null,
  lastSaved: null,
  isDirty: false,
};

function documentReducer(state: DocumentState, action: DocumentAction): DocumentState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'SET_DOCUMENT':
      const { document, blocks, outline } = action.payload;
      return {
        ...state,
        document,
        virtualBlocks: blocks,
        outline,
        filteredBlocks: state.searchTerm ? 
          blocks.filter(block => 
            block.content.toLowerCase().includes(state.searchTerm.toLowerCase())
          ) : blocks,
        loading: false,
        error: null,
        isDirty: false,
      };
    
    case 'UPDATE_AST':
      if (!state.document) return state;
      
      const updatedDocument = {
        ...state.document,
        content_ast: action.payload,
        metadata: action.payload.metadata,
      };
      
      const newBlocks = documentService.flattenASTToBlocks(action.payload);
      const newOutline = documentService.generateOutline(action.payload);
      
      return {
        ...state,
        document: updatedDocument,
        virtualBlocks: newBlocks,
        outline: newOutline,
        filteredBlocks: state.searchTerm ? 
          newBlocks.filter(block => 
            block.content.toLowerCase().includes(state.searchTerm.toLowerCase())
          ) : newBlocks,
        isDirty: true,
      };
    
    case 'SET_EDITING_NODE':
      return { ...state, editingNodeId: action.payload };
    
    case 'SET_SEARCH_TERM':
      const searchTerm = action.payload;
      const filteredBlocks = searchTerm ? 
        state.virtualBlocks.filter(block => 
          block.content.toLowerCase().includes(searchTerm.toLowerCase())
        ) : state.virtualBlocks;
      
      return {
        ...state,
        searchTerm,
        filteredBlocks,
      };
    
    case 'UPDATE_NODE_CONTENT':
      if (!state.document) return state;
      
      const { nodeId, content } = action.payload;
      const updatedAST = documentService.updateNodeInAST(
        state.document.content_ast, 
        nodeId, 
        content
      );
      
      return documentReducer(state, { type: 'UPDATE_AST', payload: updatedAST });
    
    case 'SET_LAST_SAVED':
      return { ...state, lastSaved: action.payload, isDirty: false };
    
    case 'SET_DIRTY':
      return { ...state, isDirty: action.payload };
    
    default:
      return state;
  }
}

interface DocumentContextType {
  state: DocumentState;
  loadDocument: (documentId: string) => Promise<void>;
  updateNodeContent: (nodeId: string, content: string) => void;
  saveDocument: () => Promise<void>;
  setEditingNode: (nodeId: string | null) => void;
  setSearchTerm: (term: string) => void;
  insertNode: (afterNodeId: string, nodeType: string, content: string) => Promise<void>;
  deleteNode: (nodeId: string) => Promise<void>;
  updateDocumentFromMarkdown: (documentId: string, markdown: string) => Promise<void>;
  exportDocument: (format?: 'markdown' | 'html') => Promise<string>;
  searchDocument: (query: string) => Promise<any>;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const useDocument = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
};

interface DocumentProviderProps {
  children: React.ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(documentReducer, initialState);

  // Debounced save function
  const debouncedSave = useCallback(
    debounce(async (document: Document) => {
      try {
        await documentService.updateDocument(document.id, {
          content_ast: document.content_ast,
        });
        dispatch({ type: 'SET_LAST_SAVED', payload: new Date() });
      } catch (error) {
        console.error('Auto-save failed:', error);
        dispatch({ type: 'SET_ERROR', payload: 'Auto-save failed' });
      }
    }, 2000),
    []
  );

  // Auto-save when document is dirty
  useEffect(() => {
    if (state.isDirty && state.document) {
      debouncedSave(state.document);
    }
  }, [state.isDirty, state.document, debouncedSave]);

  const loadDocument = useCallback(async (documentId: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });
    
    try {
      const response = await documentService.getDocumentBlocks(documentId);
      
      dispatch({
        type: 'SET_DOCUMENT',
        payload: {
          document: response.document,
          blocks: response.blocks,
          outline: response.outline,
        },
      });
    } catch (error) {
      console.error('Failed to load document:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to load document' 
      });
    }
  }, []);

  const updateNodeContent = useCallback((nodeId: string, content: string) => {
    dispatch({ 
      type: 'UPDATE_NODE_CONTENT', 
      payload: { nodeId, content } 
    });
  }, []);

  const saveDocument = useCallback(async () => {
    if (!state.document || !state.isDirty) return;
    
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      await documentService.updateDocument(state.document.id, {
        content_ast: state.document.content_ast,
      });
      
      dispatch({ type: 'SET_LAST_SAVED', payload: new Date() });
    } catch (error) {
      console.error('Failed to save document:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to save document' 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.document, state.isDirty]);

  const setEditingNode = useCallback((nodeId: string | null) => {
    dispatch({ type: 'SET_EDITING_NODE', payload: nodeId });
  }, []);

  const setSearchTerm = useCallback((term: string) => {
    dispatch({ type: 'SET_SEARCH_TERM', payload: term });
  }, []);

  const insertNode = useCallback(async (afterNodeId: string, nodeType: string, content: string) => {
    if (!state.document) return;
    
    try {
      const operation: NodeOperation = {
        operation: 'insert',
        data: {
          position: 'after',
          node: {
            type: nodeType as any,
            content,
          },
        },
      };
      
      const updatedDocument = await documentService.updateASTNode(
        state.document.id,
        afterNodeId,
        operation
      );
      
      const blocks = documentService.flattenASTToBlocks(updatedDocument.content_ast);
      const outline = documentService.generateOutline(updatedDocument.content_ast);
      
      dispatch({
        type: 'SET_DOCUMENT',
        payload: {
          document: updatedDocument,
          blocks,
          outline,
        },
      });
    } catch (error) {
      console.error('Failed to insert node:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to insert node' 
      });
    }
  }, [state.document]);

  const deleteNode = useCallback(async (nodeId: string) => {
    if (!state.document) return;
    
    try {
      const operation: NodeOperation = {
        operation: 'delete',
        data: {},
      };
      
      const updatedDocument = await documentService.updateASTNode(
        state.document.id,
        nodeId,
        operation
      );
      
      const blocks = documentService.flattenASTToBlocks(updatedDocument.content_ast);
      const outline = documentService.generateOutline(updatedDocument.content_ast);
      
      dispatch({
        type: 'SET_DOCUMENT',
        payload: {
          document: updatedDocument,
          blocks,
          outline,
        },
      });
    } catch (error) {
      console.error('Failed to delete node:', error);
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to delete node' 
      });
    }
  }, [state.document]);

  const exportDocument = useCallback(async (format: 'markdown' | 'html' = 'markdown') => {
    if (!state.document) throw new Error('No document loaded');
    
    return await documentService.exportDocument(state.document.id, format);
  }, [state.document]);

  const updateDocumentFromMarkdown = useCallback(async (documentId: string, markdown: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // Update document with new markdown content
      const response = await documentService.updateDocumentFromMarkdown(documentId, markdown);

      // Reload the document to get updated AST and blocks
      await loadDocument(documentId);

      dispatch({ type: 'SET_DIRTY', payload: false });
      dispatch({ type: 'SET_LAST_SAVED', payload: new Date() });
    } catch (error) {
      console.error('Failed to update document from markdown:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to update document from markdown' });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [loadDocument]);

  const searchDocument = useCallback(async (query: string) => {
    if (!state.document) throw new Error('No document loaded');

    return await documentService.searchDocument(state.document.id, query);
  }, [state.document]);

  const contextValue: DocumentContextType = {
    state,
    loadDocument,
    updateNodeContent,
    saveDocument,
    setEditingNode,
    setSearchTerm,
    insertNode,
    deleteNode,
    updateDocumentFromMarkdown,
    exportDocument,
    searchDocument,
  };

  return (
    <DocumentContext.Provider value={contextValue}>
      {children}
    </DocumentContext.Provider>
  );
};
