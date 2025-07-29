import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/markdown_editor")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content_ast = Column(JSONB, nullable=False)  # Complete document AST
    raw_markdown = Column(Text)  # Original markdown for export/backup
    doc_metadata = Column(JSONB, default={})  # Document metadata (word count, page count, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes for performance with large documents
    __table_args__ = (
        Index('idx_documents_ast', 'content_ast', postgresql_using='gin'),
        Index('idx_documents_title', 'title'),
        Index('idx_documents_updated', 'updated_at'),
        Index('idx_documents_metadata', 'doc_metadata', postgresql_using='gin'),
    )

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
