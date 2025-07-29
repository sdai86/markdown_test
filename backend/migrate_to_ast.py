#!/usr/bin/env python3
"""
Migration script to convert existing block-based documents to AST format.
This script reads existing documents and blocks, converts them to AST structure,
and updates the database schema.
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, Document
from services.ast_service import ASTService

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/markdown_editor")

def create_ast_from_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert legacy blocks to AST structure.
    
    Args:
        blocks: List of block dictionaries from old schema
        
    Returns:
        AST dictionary
    """
    ast_service = ASTService()
    
    # Sort blocks by order_index
    sorted_blocks = sorted(blocks, key=lambda b: b.get('order_index', 0))
    
    # Convert blocks to markdown first
    markdown_lines = []
    
    for block in sorted_blocks:
        content = block.get('raw_content') or block.get('content', '')
        block_type = block.get('type', 'paragraph')
        level = block.get('level', 0)
        
        if block_type == 'heading':
            # Use level to determine heading size
            heading_level = min(max(level, 1), 6)
            markdown_lines.append(f"{'#' * heading_level} {content}")
        elif block_type == 'code_block':
            markdown_lines.append(f"```\n{content}\n```")
        elif block_type == 'list_item':
            # Simple list item
            markdown_lines.append(f"- {content}")
        elif block_type == 'blockquote':
            # Quote each line
            quoted_lines = [f"> {line}" for line in content.split('\n')]
            markdown_lines.extend(quoted_lines)
        else:
            # Default to paragraph
            markdown_lines.append(content)
        
        # Add spacing between blocks
        markdown_lines.append("")
    
    # Join all markdown
    full_markdown = '\n'.join(markdown_lines).strip()
    
    # Parse to AST
    if full_markdown:
        return ast_service.parse_markdown_to_ast(full_markdown)
    else:
        return ast_service._create_empty_document()

def create_sample_ast_document(db):
    """Create a sample AST document for testing."""
    print("Creating sample AST document...")
    
    sample_markdown = """# Sample AST Document

This is a sample document to demonstrate the AST-based markdown editor.

## Introduction

The AST-based approach provides several advantages:

- **Efficient storage**: Single document per database row
- **Rich operations**: Support for structural editing
- **Scalability**: Handles millions of documents efficiently

## Code Example

Here's a simple Python function:

```python
def hello_world():
    print("Hello, AST-based world!")
    return "success"
```

## Conclusion

> The AST approach represents a significant improvement in both performance and functionality.

This concludes our sample document.
"""
    
    ast_service = ASTService()
    content_ast = ast_service.parse_markdown_to_ast(sample_markdown)
    
    # Use the same document ID as the original sample
    sample_id = "550e8400-e29b-41d4-a716-446655440000"
    
    db.execute(text("""
        INSERT INTO documents (id, title, content_ast, raw_markdown, doc_metadata, created_at, updated_at)
        VALUES (:id, :title, :content_ast, :raw_markdown, :doc_metadata, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET
            content_ast = EXCLUDED.content_ast,
            raw_markdown = EXCLUDED.raw_markdown,
            doc_metadata = EXCLUDED.doc_metadata,
            updated_at = NOW()
    """), {
        "id": sample_id,
        "title": "Sample AST Document",
        "content_ast": json.dumps(content_ast),
        "raw_markdown": sample_markdown,
        "doc_metadata": json.dumps(content_ast.get('metadata', {}))
    })
    
    db.commit()
    print(f"✓ Created sample document with ID: {sample_id}")

def migrate_documents():
    """
    Main migration function to convert all documents to AST format.
    """
    print("Starting migration to AST-based documents...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create new tables
    print("Creating new database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if old tables exist
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('documents', 'blocks')
        """))
        
        existing_tables = [row[0] for row in result.fetchall()]
        
        if 'blocks' not in existing_tables:
            print("No legacy blocks table found. Creating sample AST document...")
            create_sample_ast_document(db)
            return
        
        # Get all documents from old schema
        print("Fetching existing documents...")
        old_documents = db.execute(text("""
            SELECT id, title, filename, total_blocks, created_at, updated_at
            FROM documents
        """)).fetchall()
        
        print(f"Found {len(old_documents)} documents to migrate")
        
        migrated_count = 0
        
        for old_doc in old_documents:
            doc_id = old_doc[0]
            title = old_doc[1]
            created_at = old_doc[4]
            updated_at = old_doc[5]
            
            print(f"Migrating document: {title} ({doc_id})")
            
            # Get all blocks for this document
            blocks_result = db.execute(text("""
                SELECT id, type, content, raw_content, order_index, level, parent_id, block_metadata
                FROM blocks 
                WHERE document_id = :doc_id
                ORDER BY order_index
            """), {"doc_id": doc_id})
            
            blocks = []
            for block_row in blocks_result.fetchall():
                blocks.append({
                    'id': block_row[0],
                    'type': block_row[1],
                    'content': block_row[2],
                    'raw_content': block_row[3],
                    'order_index': block_row[4],
                    'level': block_row[5],
                    'parent_id': block_row[6],
                    'metadata': json.loads(block_row[7]) if block_row[7] else {}
                })
            
            print(f"  Converting {len(blocks)} blocks to AST...")
            
            # Convert blocks to AST
            content_ast = create_ast_from_blocks(blocks)
            
            # Generate raw markdown from AST
            ast_service = ASTService()
            raw_markdown = ast_service.ast_to_markdown(content_ast)
            
            # Check if document already exists in new format
            existing_doc = db.execute(text("""
                SELECT id FROM documents WHERE id = :doc_id
            """), {"doc_id": doc_id}).fetchone()
            
            if existing_doc:
                # Update existing document
                db.execute(text("""
                    UPDATE documents
                    SET content_ast = :content_ast,
                        raw_markdown = :raw_markdown,
                        doc_metadata = :doc_metadata,
                        updated_at = :updated_at
                    WHERE id = :doc_id
                """), {
                    "doc_id": doc_id,
                    "content_ast": json.dumps(content_ast),
                    "raw_markdown": raw_markdown,
                    "doc_metadata": json.dumps(content_ast.get('metadata', {})),
                    "updated_at": updated_at
                })
            else:
                # Insert new document
                db.execute(text("""
                    INSERT INTO documents (id, title, content_ast, raw_markdown, doc_metadata, created_at, updated_at)
                    VALUES (:id, :title, :content_ast, :raw_markdown, :doc_metadata, :created_at, :updated_at)
                """), {
                    "id": doc_id,
                    "title": title,
                    "content_ast": json.dumps(content_ast),
                    "raw_markdown": raw_markdown,
                    "doc_metadata": json.dumps(content_ast.get('metadata', {})),
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            
            migrated_count += 1
            print(f"  ✓ Migrated document {title}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Migration completed successfully!")
        print(f"   Migrated {migrated_count} documents")
        print(f"   Old blocks table can be safely dropped if migration is verified")
        
        # Optionally rename old tables
        print("\nRenaming old tables for backup...")
        db.execute(text("ALTER TABLE blocks RENAME TO blocks_backup"))
        db.commit()
        print("   ✓ Renamed 'blocks' table to 'blocks_backup'")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_documents()
