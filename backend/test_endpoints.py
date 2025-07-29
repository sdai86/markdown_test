import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from main import app
from database import get_db, Base, Document, Block

# Test database setup - use PostgreSQL for UUID support
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/markdown_editor"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_document(client):
    """Create a sample document for testing."""
    response = client.post("/documents", json={
        "title": "Test Document",
        "filename": "test.md"
    })
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def sample_blocks(client, sample_document):
    """Create sample blocks for testing."""
    document_id = sample_document["id"]
    
    # Parse some sample markdown
    markdown_content = """# Test Heading 1

This is a paragraph with some content.

## Test Heading 2

Another paragraph here.

```python
def hello_world():
    print("Hello, World!")
```

> This is a blockquote
> with multiple lines.

- List item 1
- List item 2
- List item 3
"""
    
    response = client.post(f"/documents/{document_id}/parse", json={
        "markdown_content": markdown_content
    })
    assert response.status_code == 200
    return response.json()

class TestHealthEndpoint:
    def test_health_check(self, client, setup_database):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestDocumentEndpoints:
    def test_create_document(self, client, setup_database):
        response = client.post("/documents", json={
            "title": "Test Document",
            "filename": "test.md"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Document"
        assert data["filename"] == "test.md"
        assert "id" in data

    def test_get_documents(self, client, setup_database, sample_document):
        response = client.get("/documents")
        assert response.status_code == 200
        documents = response.json()
        assert len(documents) >= 1
        assert any(doc["id"] == sample_document["id"] for doc in documents)

class TestBlockEndpoints:
    def test_get_blocks(self, client, setup_database, sample_blocks):
        response = client.get("/blocks")
        assert response.status_code == 200
        data = response.json()
        assert "blocks" in data
        assert "total" in data
        assert data["total"] > 0

    def test_get_blocks_with_pagination(self, client, setup_database, sample_blocks):
        response = client.get("/blocks?offset=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["blocks"]) <= 2
        assert data["offset"] == 0
        assert data["limit"] == 2

    def test_get_blocks_by_document(self, client, setup_database, sample_document, sample_blocks):
        document_id = sample_document["id"]
        response = client.get(f"/blocks?document_id={document_id}")
        assert response.status_code == 200
        data = response.json()
        assert all(block["document_id"] == document_id for block in data["blocks"])

    def test_update_block(self, client, setup_database, sample_blocks):
        # Get first block
        response = client.get("/blocks?limit=1")
        assert response.status_code == 200
        block = response.json()["blocks"][0]
        block_id = block["id"]
        
        # Update the block
        new_content = "Updated content"
        new_raw_content = "# Updated markdown content"
        
        response = client.patch(f"/blocks/{block_id}", json={
            "content": new_content,
            "raw_content": new_raw_content
        })
        assert response.status_code == 200
        updated_block = response.json()
        assert updated_block["content"] == new_content
        assert updated_block["raw_content"] == new_raw_content

class TestTOCEndpoint:
    def test_get_toc(self, client, setup_database, sample_blocks):
        response = client.get("/toc")
        assert response.status_code == 200
        toc = response.json()
        assert isinstance(toc, list)
        # Should have at least 2 headings from sample data
        assert len(toc) >= 2
        
        # Check structure
        for item in toc:
            assert "id" in item
            assert "text" in item
            assert "level" in item
            assert "order_index" in item

    def test_get_toc_by_document(self, client, setup_database, sample_document, sample_blocks):
        document_id = sample_document["id"]
        response = client.get(f"/toc?document_id={document_id}")
        assert response.status_code == 200
        toc = response.json()
        assert isinstance(toc, list)
        assert len(toc) >= 2

class TestExportEndpoint:
    def test_export_markdown(self, client, setup_database, sample_blocks):
        response = client.get("/export")
        assert response.status_code == 200
        data = response.json()
        
        assert "markdown" in data
        assert "total_blocks" in data
        assert "export_time_ms" in data
        
        # Check that markdown content is not empty
        assert len(data["markdown"]) > 0
        assert data["total_blocks"] > 0
        
        # Check that exported markdown contains expected content
        markdown = data["markdown"]
        assert "# Test Heading 1" in markdown
        assert "## Test Heading 2" in markdown
        assert "```python" in markdown
        assert "def hello_world():" in markdown

    def test_export_markdown_by_document(self, client, setup_database, sample_document, sample_blocks):
        document_id = sample_document["id"]
        response = client.get(f"/export?document_id={document_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "markdown" in data
        assert data["total_blocks"] > 0

class TestMarkdownParsing:
    def test_parse_markdown_with_ast(self, client, setup_database, sample_document):
        document_id = sample_document["id"]
        markdown_content = """# AST Test

This is a test for AST parsing.

```javascript
console.log("Hello from AST!");
```
"""
        
        response = client.post(f"/documents/{document_id}/parse?use_ast=true", json={
            "markdown_content": markdown_content
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "total_blocks" in data
        assert "parse_stats" in data
        assert data["total_blocks"] > 0

    def test_parse_markdown_direct(self, client, setup_database, sample_document):
        document_id = sample_document["id"]
        markdown_content = """# Direct Parse Test

This is a test for direct parsing.
"""
        
        response = client.post(f"/documents/{document_id}/parse?use_ast=false", json={
            "markdown_content": markdown_content
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "total_blocks" in data
        assert data["total_blocks"] > 0

class TestPerformanceEndpoints:
    def test_performance_metrics(self, client, setup_database):
        response = client.get("/performance/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert isinstance(metrics, list)

    def test_clear_performance_logs(self, client, setup_database):
        response = client.delete("/performance/clear")
        assert response.status_code == 200
        assert response.json() == {"message": "Performance logs cleared"}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
