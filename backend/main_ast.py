"""
AST-based Markdown Editor API
FastAPI application with AST document management
"""

import time
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, create_tables, Document
from services.document_service import DocumentService
from services.ast_service import ASTService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
document_service = DocumentService()
ast_service = ASTService()

# Pydantic models for API
class DocumentCreate(BaseModel):
    title: str
    markdown_content: str = ""

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content_ast: Optional[Dict[str, Any]] = None
    raw_markdown: Optional[str] = None

class NodeOperation(BaseModel):
    operation: str  # update, insert, delete, move
    data: Dict[str, Any]

class DocumentResponse(BaseModel):
    id: str
    title: str
    content_ast: Dict[str, Any]
    raw_markdown: Optional[str]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

class VirtualBlock(BaseModel):
    id: str
    type: str
    content: str
    level: Optional[int] = None
    astPath: List[int]
    depth: int
    position: Optional[Dict[str, Any]] = None
    isCollapsible: bool = False
    isCollapsed: bool = False

class DocumentBlocksResponse(BaseModel):
    document: DocumentResponse
    blocks: List[VirtualBlock]
    outline: List[Dict[str, Any]]

# FastAPI app
app = FastAPI(title="AST-based Markdown Editor API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.4f}s")
    return response

@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created for AST-based documents")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "type": "ast-based"}

# Document CRUD endpoints
@app.post("/documents", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document from markdown content."""
    try:
        document = await document_service.create_document(
            db, document_data.title, document_data.markdown_content
        )
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            content_ast=document.content_ast,
            raw_markdown=document.raw_markdown,
            metadata=document.doc_metadata,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List documents with pagination."""
    try:
        documents = await document_service.list_documents(db, skip, limit)
        
        return [
            DocumentResponse(
                id=str(doc.id),
                title=doc.title,
                content_ast=doc.content_ast,
                raw_markdown=doc.raw_markdown,
                metadata=doc.doc_metadata,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat()
            )
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get a document by ID."""
    try:
        document = await document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            content_ast=document.content_ast,
            raw_markdown=document.raw_markdown,
            metadata=document.doc_metadata,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update a document."""
    try:
        document = await document_service.update_document(
            db, document_id, 
            title=update_data.title,
            content_ast=update_data.content_ast,
            raw_markdown=update_data.raw_markdown
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            content_ast=document.content_ast,
            raw_markdown=document.raw_markdown,
            metadata=document.doc_metadata,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document."""
    try:
        success = await document_service.delete_document(db, document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AST node operations
@app.patch("/documents/{document_id}/nodes/{node_id}", response_model=DocumentResponse)
async def update_ast_node(
    document_id: str,
    node_id: str,
    operation: NodeOperation,
    db: Session = Depends(get_db)
):
    """Update a specific AST node in a document."""
    try:
        document = await document_service.update_ast_node(
            db, document_id, node_id, operation.operation, operation.data
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            content_ast=document.content_ast,
            raw_markdown=document.raw_markdown,
            metadata=document.doc_metadata,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating node {node_id} in document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/update-from-markdown", response_model=DocumentResponse)
async def update_document_from_markdown(
    document_id: str,
    request: dict,
    db: Session = Depends(get_db)
):
    """Update entire document from raw markdown content."""
    try:
        markdown = request.get("markdown", "")
        if not markdown:
            raise HTTPException(status_code=400, detail="Markdown content is required")

        document = await document_service.update_document_from_markdown(db, document_id, markdown)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            content_ast=document.content_ast,
            raw_markdown=document.raw_markdown,
            metadata=document.doc_metadata,
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to update document from markdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Document rendering endpoints
@app.get("/documents/{document_id}/blocks", response_model=DocumentBlocksResponse)
async def get_document_blocks(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get document with flattened blocks for frontend rendering."""
    try:
        document = await document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Flatten AST to virtual blocks
        blocks = document_service.flatten_ast_to_blocks(document)
        
        # Generate outline
        outline = document_service.get_document_outline(document)
        
        return DocumentBlocksResponse(
            document=DocumentResponse(
                id=str(document.id),
                title=document.title,
                content_ast=document.content_ast,
                raw_markdown=document.raw_markdown,
                metadata=document.doc_metadata,
                created_at=document.created_at.isoformat(),
                updated_at=document.updated_at.isoformat()
            ),
            blocks=[VirtualBlock(**block) for block in blocks],
            outline=outline
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blocks for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}/outline")
async def get_document_outline(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get document outline (Table of Contents)."""
    try:
        document = await document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        outline = document_service.get_document_outline(document)
        return {"outline": outline}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting outline for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export endpoints
@app.get("/documents/{document_id}/export")
async def export_document(
    document_id: str,
    format: str = Query("markdown", regex="^(markdown|html)$"),
    db: Session = Depends(get_db)
):
    """Export document in specified format."""
    try:
        content = await document_service.export_document(db, document_id, format)
        if content is None:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"content": content, "format": format}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoints
@app.get("/documents/{document_id}/search")
async def search_document(
    document_id: str,
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search within a document."""
    try:
        document = await document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        matches = document_service.search_document_content(document, q)
        return {"query": q, "matches": matches}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
