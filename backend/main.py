import time
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, create_tables, Document, Block
from schemas import (
    BlockCreate, BlockUpdate, Block as BlockSchema, 
    DocumentCreate, Document as DocumentSchema,
    BlocksResponse, TOCItem, PerformanceLog
)
from markdown_parser import MarkdownParser
from performance_logger import perf_logger, measure_time, PerformanceMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Markdown Editor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parser
parser = MarkdownParser(use_ast=False)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/performance/metrics")
async def get_performance_metrics():
    """Get collected performance metrics."""
    return {
        "metrics": perf_logger.get_metrics(),
        "summary": perf_logger.get_summary()
    }

@app.post("/performance/clear")
async def clear_performance_metrics():
    """Clear collected performance metrics."""
    perf_logger.clear_metrics()
    return {"status": "cleared"}

@app.get("/blocks", response_model=BlocksResponse)
async def get_blocks(
    document_id: Optional[UUID] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get paginated blocks with performance logging."""
    start_time = time.time()
    
    query = db.query(Block)
    if document_id:
        query = query.filter(Block.document_id == document_id)
    
    query = query.order_by(Block.order_index)
    total = query.count()
    blocks = query.offset(offset).limit(limit).all()
    
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Retrieved {len(blocks)} blocks in {duration_ms:.2f}ms")
    
    return BlocksResponse(
        blocks=blocks,
        total=total,
        offset=offset,
        limit=limit
    )

@app.get("/blocks/{block_id}", response_model=BlockSchema)
async def get_block(block_id: UUID, db: Session = Depends(get_db)):
    """Get a specific block by ID."""
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

@app.patch("/blocks/{block_id}", response_model=BlockSchema)
async def update_block(
    block_id: UUID, 
    block_update: BlockUpdate, 
    db: Session = Depends(get_db)
):
    """Update a specific block with performance logging."""
    start_time = time.time()
    
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    # Update fields
    update_data = block_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(block, field, value)
    
    db.commit()
    db.refresh(block)
    
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Updated block {block_id} in {duration_ms:.2f}ms")
    
    return block

@app.get("/toc")
async def get_table_of_contents(
    document_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
) -> List[TOCItem]:
    """Get table of contents from heading blocks."""
    start_time = time.time()
    
    query = db.query(Block).filter(Block.type == 'heading')
    if document_id:
        query = query.filter(Block.document_id == document_id)
    
    headings = query.order_by(Block.order_index).all()
    
    toc = [
        TOCItem(
            id=heading.id,
            text=heading.content,
            level=heading.level,
            order_index=heading.order_index
        )
        for heading in headings
    ]
    
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Generated ToC with {len(toc)} items in {duration_ms:.2f}ms")
    
    return toc

@app.get("/export")
async def export_markdown(
    document_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Export blocks back to markdown format."""
    start_time = time.time()

    query = db.query(Block)
    if document_id:
        query = query.filter(Block.document_id == document_id)

    blocks = query.order_by(Block.order_index).all()

    # Convert to ParsedBlock format for the parser
    from markdown_parser import ParsedBlock
    parsed_blocks = [
        ParsedBlock(
            type=block.type,
            content=block.content,
            raw_content=block.raw_content or block.content,
            level=block.level,
            order_index=block.order_index,
            metadata=block.metadata or {}
        )
        for block in blocks
    ]

    markdown_content = parser.blocks_to_markdown(parsed_blocks)

    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Exported {len(blocks)} blocks to markdown in {duration_ms:.2f}ms")

    return {
        "markdown": markdown_content,
        "total_blocks": len(blocks),
        "export_time_ms": duration_ms
    }

@app.post("/documents", response_model=DocumentSchema)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document."""
    db_document = Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@app.post("/documents/{document_id}/parse")
async def parse_markdown_file(
    document_id: UUID,
    markdown_content: str,
    use_ast: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Parse markdown content and store as blocks."""
    start_time = time.time()

    # Check if document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clear existing blocks
    db.query(Block).filter(Block.document_id == document_id).delete()

    # Parse markdown
    parser.use_ast = use_ast
    parsed_blocks, parse_stats = parser.parse_markdown(markdown_content)

    # Store blocks in database
    db_blocks = []
    for parsed_block in parsed_blocks:
        db_block = Block(
            type=parsed_block.type,
            content=parsed_block.content,
            raw_content=parsed_block.raw_content,
            order_index=parsed_block.order_index,
            level=parsed_block.level,
            document_id=document_id,
            metadata=parsed_block.metadata
        )
        db_blocks.append(db_block)

    db.add_all(db_blocks)

    # Update document total_blocks
    document.total_blocks = len(db_blocks)
    db.commit()

    total_time_ms = (time.time() - start_time) * 1000

    logger.info(f"Parsed and stored {len(db_blocks)} blocks in {total_time_ms:.2f}ms")

    return {
        "document_id": document_id,
        "total_blocks": len(db_blocks),
        "parse_stats": parse_stats,
        "total_time_ms": total_time_ms
    }

@app.get("/documents", response_model=List[DocumentSchema])
async def get_documents(db: Session = Depends(get_db)):
    """Get all documents."""
    return db.query(Document).all()

@app.get("/documents/{document_id}", response_model=DocumentSchema)
async def get_document(document_id: UUID, db: Session = Depends(get_db)):
    """Get a specific document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
