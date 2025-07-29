/**
 * AST-based Document Service
 * Handles API communication for AST-based documents
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface DocumentAST {
  type: 'document';
  children: ASTNode[];
  metadata: {
    wordCount: number;
    nodeCount: number;
    pageCount: number;
  };
}

export interface ASTNode {
  id: string;
  type: 'heading' | 'paragraph' | 'list' | 'list_item' | 'code_block' | 'blockquote' | 'horizontal_rule';
  content: string;
  level?: number;
  listType?: 'ordered' | 'unordered';
  language?: string;
  position?: {
    line: number;
    column: number;
  };
  children?: ASTNode[];
}

export interface Document {
  id: string;
  title: string;
  content_ast: DocumentAST;
  raw_markdown?: string;
  metadata: {
    wordCount: number;
    nodeCount: number;
    pageCount: number;
  };
  created_at: string;
  updated_at: string;
}

export interface VirtualBlock {
  id: string;
  type: string;
  content: string;
  level?: number;
  astPath: number[];
  depth: number;
  position?: {
    line: number;
    column: number;
  };
  isCollapsible: boolean;
  isCollapsed: boolean;
  listType?: string;
  language?: string;
}

export interface DocumentBlocksResponse {
  document: Document;
  blocks: VirtualBlock[];
  outline: OutlineItem[];
}

export interface OutlineItem {
  id: string;
  title: string;
  level: number;
  depth: number;
}

export interface NodeOperation {
  operation: 'update' | 'insert' | 'delete' | 'move';
  data: {
    content?: string;
    position?: 'before' | 'after';
    node?: Partial<ASTNode>;
    target_id?: string;
  };
}

export interface SearchResult {
  query: string;
  matches: Array<{
    id: string;
    type: string;
    content: string;
    level?: number;
    match_context: string;
  }>;
}

class DocumentService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds for large documents
  });

  constructor() {
    // Add request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging
    this.api.interceptors.response.use(
      (response) => {
        const processTime = response.headers['x-process-time'];
        if (processTime) {
          console.log(`API Response: ${response.config.url} - ${processTime}s`);
        }
        return response;
      },
      (error) => {
        console.error('API Response Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Document CRUD operations
  async createDocument(title: string, markdownContent: string = ''): Promise<Document> {
    const response = await this.api.post('/documents', {
      title,
      markdown_content: markdownContent,
    });
    return response.data;
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await this.api.get(`/documents/${documentId}`);
    return response.data;
  }

  async listDocuments(skip: number = 0, limit: number = 100): Promise<Document[]> {
    const response = await this.api.get('/documents', {
      params: { skip, limit },
    });
    return response.data;
  }

  async updateDocument(
    documentId: string,
    updates: {
      title?: string;
      content_ast?: DocumentAST;
      raw_markdown?: string;
    }
  ): Promise<Document> {
    const response = await this.api.put(`/documents/${documentId}`, updates);
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.api.delete(`/documents/${documentId}`);
  }

  // AST node operations
  async updateASTNode(
    documentId: string,
    nodeId: string,
    operation: NodeOperation
  ): Promise<Document> {
    const response = await this.api.patch(
      `/documents/${documentId}/nodes/${nodeId}`,
      operation
    );
    return response.data;
  }

  // Document rendering
  async getDocumentBlocks(documentId: string): Promise<DocumentBlocksResponse> {
    const response = await this.api.get(`/documents/${documentId}/blocks`);
    return response.data;
  }

  async getDocumentOutline(documentId: string): Promise<OutlineItem[]> {
    const response = await this.api.get(`/documents/${documentId}/outline`);
    return response.data.outline;
  }

  // Export
  async exportDocument(documentId: string, format: 'markdown' | 'html' = 'markdown'): Promise<string> {
    const response = await this.api.get(`/documents/${documentId}/export`, {
      params: { format },
    });
    return response.data.content;
  }

  // Search
  async searchDocument(documentId: string, query: string): Promise<SearchResult> {
    const response = await this.api.get(`/documents/${documentId}/search`, {
      params: { q: query },
    });
    return response.data;
  }

  // Utility methods for AST manipulation
  findNodeInAST(ast: DocumentAST, nodeId: string): ASTNode | null {
    const searchNode = (node: ASTNode): ASTNode | null => {
      if (node.id === nodeId) {
        return node;
      }
      
      if (node.children) {
        for (const child of node.children) {
          const result = searchNode(child);
          if (result) return result;
        }
      }
      
      return null;
    };

    for (const child of ast.children) {
      const result = searchNode(child);
      if (result) return result;
    }
    
    return null;
  }

  getNodePath(ast: DocumentAST, nodeId: string): number[] {
    const findPath = (node: ASTNode, path: number[] = []): number[] | null => {
      if (node.id === nodeId) {
        return path;
      }
      
      if (node.children) {
        for (let i = 0; i < node.children.length; i++) {
          const result = findPath(node.children[i], [...path, i]);
          if (result) return result;
        }
      }
      
      return null;
    };

    for (let i = 0; i < ast.children.length; i++) {
      const result = findPath(ast.children[i], [i]);
      if (result) return result;
    }
    
    return [];
  }

  // Helper method to update node content locally (for optimistic updates)
  updateNodeInAST(ast: DocumentAST, nodeId: string, content: string): DocumentAST {
    const updatedAST = JSON.parse(JSON.stringify(ast)); // Deep clone
    
    const updateNode = (node: ASTNode): boolean => {
      if (node.id === nodeId) {
        node.content = content;
        return true;
      }
      
      if (node.children) {
        for (const child of node.children) {
          if (updateNode(child)) return true;
        }
      }
      
      return false;
    };

    for (const child of updatedAST.children) {
      if (updateNode(child)) break;
    }
    
    return updatedAST;
  }

  // Generate virtual blocks from AST (for frontend rendering)
  flattenASTToBlocks(ast: DocumentAST): VirtualBlock[] {
    const blocks: VirtualBlock[] = [];
    
    const flattenNodes = (nodes: ASTNode[], path: number[] = [], depth: number = 0) => {
      nodes.forEach((node, index) => {
        const currentPath = [...path, index];
        
        blocks.push({
          id: node.id,
          type: node.type,
          content: node.content,
          level: node.level,
          astPath: currentPath,
          depth,
          position: node.position,
          isCollapsible: node.type === 'heading',
          isCollapsed: false,
          listType: node.listType,
          language: node.language,
        });
        
        if (node.children) {
          flattenNodes(node.children, currentPath, depth + 1);
        }
      });
    };
    
    flattenNodes(ast.children);
    return blocks;
  }

  // Generate outline from AST
  generateOutline(ast: DocumentAST): OutlineItem[] {
    const outline: OutlineItem[] = [];
    
    const extractHeadings = (nodes: ASTNode[], depth: number = 0) => {
      nodes.forEach((node) => {
        if (node.type === 'heading') {
          outline.push({
            id: node.id,
            title: node.content,
            level: node.level || 1,
            depth,
          });
        }
        
        if (node.children) {
          extractHeadings(node.children, depth + 1);
        }
      });
    };
    
    extractHeadings(ast.children);
    return outline;
  }
}

export const documentService = new DocumentService();
export default documentService;
