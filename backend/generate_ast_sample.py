#!/usr/bin/env python3
"""
Generate large AST-based sample document
Creates a comprehensive markdown document and stores it in AST format
"""

import os
import sys
import json
import uuid
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, Document
from services.ast_service import ASTService

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/markdown_editor")

def generate_large_markdown_content(target_pages: int = 300) -> str:
    """Generate a large markdown document with approximately target_pages pages."""
    
    lines = []
    
    # Title and introduction
    lines.extend([
        "# The Complete Guide to Software Engineering",
        "",
        "This is a comprehensive guide covering all aspects of modern software engineering.",
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} with target of {target_pages}+ pages.",
        "",
        "## Table of Contents",
        "",
        "This document covers the following major topics:",
        "",
        "- Software Development Methodologies",
        "- Programming Languages and Frameworks", 
        "- Database Design and Management",
        "- System Architecture and Design Patterns",
        "- Testing and Quality Assurance",
        "- DevOps and Deployment Strategies",
        "- Security Best Practices",
        "- Performance Optimization",
        "- Project Management",
        "- Team Collaboration",
        "",
    ])
    
    # Generate content for each major section
    sections = [
        "Software Development Methodologies",
        "Programming Languages and Frameworks",
        "Database Design and Management", 
        "System Architecture and Design Patterns",
        "Testing and Quality Assurance",
        "DevOps and Deployment Strategies",
        "Security Best Practices",
        "Performance Optimization",
        "Project Management",
        "Team Collaboration"
    ]
    
    for section_idx, section in enumerate(sections, 1):
        lines.extend([
            f"# {section_idx}. {section}",
            "",
            f"This section provides comprehensive coverage of {section.lower()}.",
            "",
        ])
        
        # Generate subsections
        for subsection_idx in range(1, 21):  # 20 subsections per section
            subsection_title = f"{section_idx}.{subsection_idx} {section} - Part {subsection_idx}"
            lines.extend([
                f"## {subsection_title}",
                "",
                f"This subsection covers important aspects of {section.lower()} part {subsection_idx}.",
                "",
            ])
            
            # Generate sub-subsections
            for subsubsection_idx in range(1, 6):  # 5 sub-subsections per subsection
                subsubsection_title = f"Key Concept #{subsubsection_idx}"
                lines.extend([
                    f"### {section_idx}.{subsection_idx}.{subsubsection_idx} {subsubsection_title}",
                    "",
                    f"Understanding {subsubsection_title.lower()} is crucial for mastering {section.lower()}.",
                    "",
                    "Key points to remember:",
                    "",
                ])
                
                # Generate bullet points
                for point_idx in range(1, 8):  # 7 bullet points
                    lines.append(f"- Important consideration #{point_idx} for {subsubsection_title.lower()}")
                
                lines.extend([
                    "",
                    "### Implementation Details",
                    "",
                    "Here's how to implement this concept:",
                    "",
                    "```python",
                    f"def implement_{section.lower().replace(' ', '_')}_concept_{subsubsection_idx}():",
                    f'    """Implement {subsubsection_title.lower()} for {section.lower()}."""',
                    "    # Step 1: Initialize the system",
                    "    system = initialize_system()",
                    "    ",
                    "    # Step 2: Configure parameters", 
                    f"    config = configure_parameters(concept_id={subsubsection_idx})",
                    "    ",
                    "    # Step 3: Execute implementation",
                    "    result = system.execute(config)",
                    "    ",
                    "    # Step 4: Validate results",
                    "    if validate_results(result):",
                    '        return {"status": "success", "result": result}',
                    "    else:",
                    '        raise Exception("Implementation failed validation")',
                    "```",
                    "",
                    "### Best Practices",
                    "",
                    f"When working with {subsubsection_title.lower()}, consider these best practices:",
                    "",
                ])
                
                # Generate numbered list
                for practice_idx in range(1, 6):  # 5 best practices
                    lines.append(f"{practice_idx}. Best practice #{practice_idx} for {subsubsection_title.lower()}")
                
                lines.extend([
                    "",
                    "> **Important Note**: Always remember that proper implementation of these concepts",
                    f"> requires careful consideration of the specific requirements for {section.lower()}.",
                    "",
                    "### Common Pitfalls",
                    "",
                    "Avoid these common mistakes:",
                    "",
                ])
                
                # Generate warning list
                for warning_idx in range(1, 4):  # 3 warnings
                    lines.append(f"⚠️ **Warning #{warning_idx}**: Common pitfall when implementing {subsubsection_title.lower()}")
                
                lines.extend([
                    "",
                    "---",
                    "",
                ])
    
    # Add conclusion
    lines.extend([
        "# Conclusion",
        "",
        "This comprehensive guide has covered all major aspects of modern software engineering.",
        "By following the principles and practices outlined in this document, you will be well-equipped",
        "to tackle complex software development challenges.",
        "",
        "## Summary of Key Points",
        "",
        "The most important takeaways from this guide include:",
        "",
    ])
    
    # Generate summary points
    for summary_idx in range(1, 21):  # 20 summary points
        lines.append(f"- Key takeaway #{summary_idx}: Essential principle for software engineering success")
    
    lines.extend([
        "",
        "## Next Steps",
        "",
        "To continue your software engineering journey:",
        "",
        "1. Practice implementing the concepts covered in this guide",
        "2. Stay updated with the latest industry trends and technologies", 
        "3. Contribute to open-source projects to gain real-world experience",
        "4. Build a portfolio of diverse software projects",
        "5. Network with other software engineering professionals",
        "",
        "---",
        "",
        f"*Document generated on {datetime.now().isoformat()}*",
        f"*Total estimated pages: {target_pages}+*",
        ""
    ])
    
    return '\n'.join(lines)

def create_large_ast_document():
    """Create a large AST-based document in the database."""
    print("🚀 Generating large AST-based sample document...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Generate large markdown content
        print("📝 Generating markdown content...")
        markdown_content = generate_large_markdown_content(target_pages=300)
        
        print(f"✅ Generated {len(markdown_content)} characters of markdown")
        print(f"📄 Estimated {len(markdown_content.split())} words")
        
        # Parse to AST
        print("🔄 Parsing markdown to AST...")
        ast_service = ASTService()
        content_ast = ast_service.parse_markdown_to_ast(markdown_content)
        
        print(f"✅ Created AST with {content_ast['metadata']['nodeCount']} nodes")
        print(f"📊 Metadata: {content_ast['metadata']['wordCount']} words, {content_ast['metadata']['pageCount']} pages")
        
        # Create document ID
        large_doc_id = "550e8400-e29b-41d4-a716-446655440001"  # Different from sample
        
        # Check if document already exists
        existing = db.execute(text("SELECT id FROM documents WHERE id = :id"), {"id": large_doc_id}).fetchone()
        
        if existing:
            print("📝 Updating existing large document...")
            db.execute(text("""
                UPDATE documents 
                SET title = :title,
                    content_ast = :content_ast,
                    raw_markdown = :raw_markdown,
                    doc_metadata = :doc_metadata,
                    updated_at = NOW()
                WHERE id = :id
            """), {
                "id": large_doc_id,
                "title": "The Complete Guide to Software Engineering (300+ Pages)",
                "content_ast": json.dumps(content_ast),
                "raw_markdown": markdown_content,
                "doc_metadata": json.dumps(content_ast.get('metadata', {}))
            })
        else:
            print("📝 Creating new large document...")
            db.execute(text("""
                INSERT INTO documents (id, title, content_ast, raw_markdown, doc_metadata, created_at, updated_at)
                VALUES (:id, :title, :content_ast, :raw_markdown, :doc_metadata, NOW(), NOW())
            """), {
                "id": large_doc_id,
                "title": "The Complete Guide to Software Engineering (300+ Pages)",
                "content_ast": json.dumps(content_ast),
                "raw_markdown": markdown_content,
                "doc_metadata": json.dumps(content_ast.get('metadata', {}))
            })
        
        db.commit()
        
        print(f"✅ Large document created successfully!")
        print(f"📄 Document ID: {large_doc_id}")
        print(f"🧱 Total AST nodes: {content_ast['metadata']['nodeCount']}")
        print(f"📊 Word count: {content_ast['metadata']['wordCount']}")
        print(f"📄 Page count: {content_ast['metadata']['pageCount']}")
        
        return large_doc_id
        
    except Exception as e:
        print(f"❌ Failed to create large document: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_large_ast_document()
