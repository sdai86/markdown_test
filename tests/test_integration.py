import pytest
import time
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import get_db, create_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Override database for testing
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Set up test database."""
    create_tables()
    yield
    # Cleanup
    os.remove("test.db") if os.path.exists("test.db") else None

def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_create_document(setup_database):
    """Test document creation."""
    start_time = time.time()
    
    response = client.post("/documents", json={
        "title": "Test Document",
        "filename": "test.md"
    })
    
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test Document"
    assert duration_ms < 100  # Should be fast
    
    return response.json()["id"]

def test_parse_large_markdown(setup_database):
    """Test parsing a large markdown document."""
    # Create a test document first
    doc_response = client.post("/documents", json={
        "title": "Large Test Document",
        "filename": "large_test.md"
    })
    document_id = doc_response.json()["id"]
    
    # Generate large markdown content (~1000 blocks)
    markdown_content = generate_large_markdown(1000)
    
    start_time = time.time()
    
    response = client.post(f"/documents/{document_id}/parse", 
                          params={"markdown_content": markdown_content})
    
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    result = response.json()
    
    # Performance requirement: parsing should complete reasonably fast
    assert duration_ms < 5000  # 5 seconds for 1000 blocks
    assert result["total_blocks"] >= 900  # Should have most blocks
    
    print(f"Parsed {result['total_blocks']} blocks in {duration_ms:.2f}ms")
    
    return document_id

def test_blocks_retrieval_performance(setup_database):
    """Test that block retrieval meets performance requirements."""
    # First create and parse a document
    document_id = test_parse_large_markdown(setup_database)
    
    # Test initial load (first 100 blocks)
    start_time = time.time()
    
    response = client.get("/blocks", params={
        "document_id": document_id,
        "offset": 0,
        "limit": 100
    })
    
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    result = response.json()
    
    # Performance requirement: < 200ms for initial load
    assert duration_ms < 200, f"Initial load took {duration_ms:.2f}ms, should be < 200ms"
    assert len(result["blocks"]) <= 100
    
    print(f"Retrieved {len(result['blocks'])} blocks in {duration_ms:.2f}ms")

def test_block_update_performance(setup_database):
    """Test that block updates meet performance requirements."""
    # Get a document with blocks
    document_id = test_parse_large_markdown(setup_database)
    
    # Get first block
    blocks_response = client.get("/blocks", params={
        "document_id": document_id,
        "offset": 0,
        "limit": 1
    })
    
    block = blocks_response.json()["blocks"][0]
    block_id = block["id"]
    
    # Test update performance
    start_time = time.time()
    
    response = client.patch(f"/blocks/{block_id}", json={
        "content": "Updated content for performance test"
    })
    
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    
    # Performance requirement: < 100ms for updates
    assert duration_ms < 100, f"Block update took {duration_ms:.2f}ms, should be < 100ms"
    
    print(f"Updated block in {duration_ms:.2f}ms")

def test_toc_generation(setup_database):
    """Test table of contents generation."""
    document_id = test_parse_large_markdown(setup_database)
    
    start_time = time.time()
    
    response = client.get("/toc", params={"document_id": document_id})
    
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    toc = response.json()
    
    # Should have headings
    assert len(toc) > 0
    assert all("text" in item and "level" in item for item in toc)
    
    print(f"Generated ToC with {len(toc)} items in {duration_ms:.2f}ms")

def test_markdown_export(setup_database):
    """Test markdown export functionality."""
    document_id = test_parse_large_markdown(setup_database)
    
    start_time = time.time()
    
    response = client.get("/export", params={"document_id": document_id})
    
    duration_ms = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    result = response.json()
    
    assert "markdown" in result
    assert "total_blocks" in result
    assert len(result["markdown"]) > 0
    
    print(f"Exported {result['total_blocks']} blocks to markdown in {duration_ms:.2f}ms")

def generate_large_markdown(num_blocks: int) -> str:
    """Generate a large markdown document for testing."""
    lines = []
    
    for i in range(num_blocks):
        if i % 20 == 0:  # Every 20th block is a heading
            level = (i // 20) % 3 + 1  # Cycle through h1, h2, h3
            lines.append(f"{'#' * level} Heading {i // 20 + 1}")
        elif i % 15 == 0:  # Every 15th block is a code block
            lines.append("```python")
            lines.append(f"def function_{i}():")
            lines.append(f"    return 'Block {i}'")
            lines.append("```")
        elif i % 10 == 0:  # Every 10th block is a blockquote
            lines.append(f"> This is a blockquote for block {i}")
        else:  # Regular paragraphs
            lines.append(f"This is paragraph {i}. It contains some sample text to make the document more realistic.")
        
        lines.append("")  # Empty line between blocks
    
    return "\n".join(lines)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
