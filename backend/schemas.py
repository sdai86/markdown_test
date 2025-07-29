from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class BlockBase(BaseModel):
    type: str
    content: str
    raw_content: Optional[str] = None
    order_index: int
    level: int = 0
    parent_id: Optional[UUID] = None
    block_metadata: Dict[str, Any] = {}

class BlockCreate(BlockBase):
    document_id: UUID

class BlockUpdate(BaseModel):
    content: Optional[str] = None
    raw_content: Optional[str] = None
    type: Optional[str] = None
    level: Optional[int] = None
    block_metadata: Optional[Dict[str, Any]] = None

class Block(BlockBase):
    id: UUID
    document_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    filename: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: UUID
    total_blocks: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentWithBlocks(Document):
    blocks: List[Block] = []

class TOCItem(BaseModel):
    id: UUID
    text: str
    level: int
    order_index: int

class BlocksResponse(BaseModel):
    blocks: List[Block]
    total: int
    offset: int
    limit: int

class PerformanceLog(BaseModel):
    operation: str
    duration_ms: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}
