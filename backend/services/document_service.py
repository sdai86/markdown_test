"""
Document Service for managing AST-based documents.
Handles CRUD operations and integrates with AST service.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import Document
from services.ast_service import ASTService
import uuid
from datetime import datetime


class DocumentService:
    def __init__(self):
        self.ast_service = ASTService()
    
    async def create_document(self, db: Session, title: str, markdown_content: str = "") -> Document:
        """
        Create a new document from markdown content.
        
        Args:
            db: Database session
            title: Document title
            markdown_content: Initial markdown content
            
        Returns:
            Created document
        """
        # Parse markdown to AST
        content_ast = self.ast_service.parse_markdown_to_ast(markdown_content)
        
        # Create document
        document = Document(
            title=title,
            content_ast=content_ast,
            raw_markdown=markdown_content,
            doc_metadata=content_ast.get("metadata", {})
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    async def get_document(self, db: Session, document_id: str) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            Document or None if not found
        """
        return db.query(Document).filter(Document.id == document_id).first()
    
    async def list_documents(self, db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        List documents with pagination.
        
        Args:
            db: Database session
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        return db.query(Document)\
                 .order_by(desc(Document.updated_at))\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    
    async def update_document(self, db: Session, document_id: str, title: str = None, 
                            content_ast: Dict[str, Any] = None, 
                            raw_markdown: str = None) -> Optional[Document]:
        """
        Update a document.
        
        Args:
            db: Database session
            document_id: Document UUID
            title: New title (optional)
            content_ast: New AST content (optional)
            raw_markdown: New raw markdown (optional)
            
        Returns:
            Updated document or None if not found
        """
        document = await self.get_document(db, document_id)
        if not document:
            return None
        
        if title is not None:
            document.title = title
        
        if content_ast is not None:
            document.content_ast = content_ast
            document.doc_metadata = content_ast.get("metadata", {})
        
        if raw_markdown is not None:
            document.raw_markdown = raw_markdown
            # If raw markdown is provided but not AST, parse it
            if content_ast is None:
                document.content_ast = self.ast_service.parse_markdown_to_ast(raw_markdown)
                document.doc_metadata = document.content_ast.get("metadata", {})
        
        db.commit()
        db.refresh(document)
        
        return document
    
    async def delete_document(self, db: Session, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            True if deleted, False if not found
        """
        document = await self.get_document(db, document_id)
        if not document:
            return False
        
        db.delete(document)
        db.commit()
        
        return True
    
    async def update_ast_node(self, db: Session, document_id: str, node_id: str, 
                            operation: str, data: Dict[str, Any]) -> Optional[Document]:
        """
        Update a specific AST node in a document.
        
        Args:
            db: Database session
            document_id: Document UUID
            node_id: AST node ID
            operation: Operation type (update, insert, delete, move)
            data: Operation data
            
        Returns:
            Updated document or None if not found
        """
        document = await self.get_document(db, document_id)
        if not document:
            return None
        
        try:
            # Update AST
            updated_ast = self.ast_service.update_ast_node(
                document.content_ast, node_id, operation, data
            )
            
            # Convert back to markdown
            updated_markdown = self.ast_service.ast_to_markdown(updated_ast)
            
            # Update document
            document.content_ast = updated_ast
            document.raw_markdown = updated_markdown
            document.doc_metadata = updated_ast.get("metadata", {})
            
            db.commit()
            db.refresh(document)
            
            return document
            
        except Exception as e:
            db.rollback()
            raise e
    
    async def export_document(self, db: Session, document_id: str, format: str = "markdown") -> Optional[str]:
        """
        Export document in specified format.
        
        Args:
            db: Database session
            document_id: Document UUID
            format: Export format (markdown, html, etc.)
            
        Returns:
            Exported content or None if document not found
        """
        document = await self.get_document(db, document_id)
        if not document:
            return None
        
        if format == "markdown":
            return document.raw_markdown or self.ast_service.ast_to_markdown(document.content_ast)
        elif format == "html":
            # Convert AST to HTML (would need additional implementation)
            return self._ast_to_html(document.content_ast)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_document_outline(self, document: Document) -> List[Dict[str, Any]]:
        """
        Generate document outline from AST (Table of Contents).
        
        Args:
            document: Document object
            
        Returns:
            List of outline items
        """
        outline = []
        
        def extract_headings(nodes, level=0):
            for node in nodes:
                if node.get("type") == "heading":
                    outline.append({
                        "id": node.get("id"),
                        "title": node.get("content", ""),
                        "level": node.get("level", 1),
                        "depth": level
                    })
                
                # Recursively process children
                if node.get("children"):
                    extract_headings(node["children"], level + 1)
        
        if document.content_ast and document.content_ast.get("children"):
            extract_headings(document.content_ast["children"])
        
        return outline
    
    def flatten_ast_to_blocks(self, document: Document) -> List[Dict[str, Any]]:
        """
        Flatten AST into virtual blocks for frontend rendering.
        
        Args:
            document: Document object
            
        Returns:
            List of virtual blocks
        """
        blocks = []
        
        def flatten_nodes(nodes, path=[], depth=0):
            for i, node in enumerate(nodes):
                current_path = path + [i]
                
                # Create virtual block
                block = {
                    "id": node.get("id"),
                    "type": node.get("type"),
                    "content": node.get("content", ""),
                    "level": node.get("level"),
                    "astPath": current_path,
                    "depth": depth,
                    "position": node.get("position"),
                    "isCollapsible": node.get("type") == "heading",
                    "isCollapsed": False
                }
                
                # Add type-specific properties
                if node.get("type") == "list":
                    block["listType"] = node.get("listType")
                elif node.get("type") == "code_block":
                    block["language"] = node.get("language")
                
                blocks.append(block)
                
                # Recursively process children
                if node.get("children"):
                    flatten_nodes(node["children"], current_path, depth + 1)
        
        if document.content_ast and document.content_ast.get("children"):
            flatten_nodes(document.content_ast["children"])
        
        return blocks
    
    def search_document_content(self, document: Document, query: str) -> List[Dict[str, Any]]:
        """
        Search for content within a document.
        
        Args:
            document: Document object
            query: Search query
            
        Returns:
            List of matching blocks with context
        """
        query_lower = query.lower()
        matches = []
        
        def search_nodes(nodes):
            for node in nodes:
                content = node.get("content", "")
                if query_lower in content.lower():
                    matches.append({
                        "id": node.get("id"),
                        "type": node.get("type"),
                        "content": content,
                        "level": node.get("level"),
                        "match_context": self._get_match_context(content, query)
                    })
                
                # Search in children
                if node.get("children"):
                    search_nodes(node["children"])
        
        if document.content_ast and document.content_ast.get("children"):
            search_nodes(document.content_ast["children"])
        
        return matches
    
    def _ast_to_html(self, ast: Dict[str, Any]) -> str:
        """Convert AST to HTML (basic implementation)."""
        # This would be a more comprehensive implementation
        # For now, convert to markdown then use a markdown-to-HTML converter
        markdown = self.ast_service.ast_to_markdown(ast)
        # Would use a library like markdown2 or similar
        return f"<html><body><pre>{markdown}</pre></body></html>"
    
    def _get_match_context(self, content: str, query: str, context_length: int = 100) -> str:
        """Get context around a search match."""
        query_lower = query.lower()
        content_lower = content.lower()
        
        match_index = content_lower.find(query_lower)
        if match_index == -1:
            return content[:context_length] + "..." if len(content) > context_length else content
        
        start = max(0, match_index - context_length // 2)
        end = min(len(content), match_index + len(query) + context_length // 2)
        
        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context

    async def update_document_from_markdown(self, db: Session, document_id: str, markdown: str) -> Optional[Document]:
        """Update entire document from raw markdown content."""
        try:
            # Get existing document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return None

            # Parse new markdown to AST
            content_ast = self.ast_service.parse_markdown_to_ast(markdown)

            # Update document
            document.content_ast = content_ast
            document.raw_markdown = markdown
            document.doc_metadata = content_ast.get('metadata', {})
            document.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(document)

            return document

        except Exception as e:
            db.rollback()
            raise e
