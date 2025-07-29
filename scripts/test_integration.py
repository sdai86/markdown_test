#!/usr/bin/env python3
"""
Integration tests for the markdown editor API endpoints.
Tests the full workflow: create document, parse markdown, update blocks, export.
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")

def test_document_creation():
    """Test document creation."""
    print("🔍 Testing document creation...")
    response = requests.post(f"{API_BASE}/documents", json={
        "title": "Integration Test Document",
        "filename": "integration_test.md"
    })
    assert response.status_code == 200
    document = response.json()
    assert "id" in document
    assert document["title"] == "Integration Test Document"
    print(f"✅ Document created with ID: {document['id']}")
    return document["id"]

def test_markdown_parsing(document_id):
    """Test markdown parsing with both AST and direct methods."""
    print("🔍 Testing markdown parsing...")
    
    test_markdown = """# Integration Test Document

This is a test document for integration testing.

## Features to Test

- Block creation and parsing
- Table of contents generation
- Export functionality
- Update synchronization

### Code Example

```python
def test_function():
    print("Hello from integration test!")
    return True
```

### Blockquote Example

> This is a blockquote to test
> multiple line parsing and
> proper block extraction.

## Performance Notes

The system should handle:
1. Fast parsing (< 100ms for small docs)
2. Efficient updates
3. Proper markdown reconstruction

### Final Section

This concludes our integration test document.
"""

    # Test AST parsing
    print("  Testing AST parsing...")
    response = requests.post(f"{API_BASE}/documents/{document_id}/parse?use_ast=true", json={
        "markdown_content": test_markdown
    })
    assert response.status_code == 200
    parse_result = response.json()
    assert parse_result["total_blocks"] > 0
    print(f"  ✅ AST parsing created {parse_result['total_blocks']} blocks")
    
    return parse_result

def test_blocks_retrieval(document_id):
    """Test block retrieval with pagination."""
    print("🔍 Testing block retrieval...")
    
    # Test basic retrieval
    response = requests.get(f"{API_BASE}/blocks?document_id={document_id}")
    assert response.status_code == 200
    data = response.json()
    assert "blocks" in data
    assert data["total"] > 0
    print(f"  ✅ Retrieved {len(data['blocks'])} blocks")
    
    # Test pagination
    response = requests.get(f"{API_BASE}/blocks?document_id={document_id}&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocks"]) <= 3
    print("  ✅ Pagination working")
    
    return data["blocks"]

def test_block_update(blocks):
    """Test block update functionality."""
    print("🔍 Testing block updates...")
    
    if not blocks:
        print("  ⚠️  No blocks to update")
        return
    
    # Update first block
    block = blocks[0]
    original_content = block["content"]
    original_raw = block.get("raw_content", "")
    
    new_content = "Updated integration test content"
    new_raw_content = "# Updated Integration Test Heading"
    
    response = requests.patch(f"{API_BASE}/blocks/{block['id']}", json={
        "content": new_content,
        "raw_content": new_raw_content
    })
    assert response.status_code == 200
    updated_block = response.json()
    
    assert updated_block["content"] == new_content
    assert updated_block["raw_content"] == new_raw_content
    print(f"  ✅ Block {block['id'][:8]}... updated successfully")
    
    # Verify the update persisted
    response = requests.get(f"{API_BASE}/blocks?document_id={block['document_id']}&limit=1")
    assert response.status_code == 200
    retrieved_block = response.json()["blocks"][0]
    assert retrieved_block["content"] == new_content
    assert retrieved_block["raw_content"] == new_raw_content
    print("  ✅ Update persistence verified")

def test_toc_generation(document_id):
    """Test table of contents generation."""
    print("🔍 Testing ToC generation...")
    
    response = requests.get(f"{API_BASE}/toc?document_id={document_id}")
    assert response.status_code == 200
    toc = response.json()
    
    assert isinstance(toc, list)
    assert len(toc) > 0
    
    # Verify ToC structure
    for item in toc:
        assert "id" in item
        assert "text" in item
        assert "level" in item
        assert "order_index" in item
    
    print(f"  ✅ ToC generated with {len(toc)} headings")
    return toc

def test_markdown_export(document_id):
    """Test markdown export functionality."""
    print("🔍 Testing markdown export...")
    
    start_time = time.time()
    response = requests.get(f"{API_BASE}/export?document_id={document_id}")
    export_time = time.time() - start_time
    
    assert response.status_code == 200
    data = response.json()
    
    assert "markdown" in data
    assert "total_blocks" in data
    assert "export_time_ms" in data
    
    markdown = data["markdown"]
    assert len(markdown) > 0
    assert data["total_blocks"] > 0
    
    # Verify exported markdown contains expected content
    markdown_lower = markdown.lower()
    assert "integration test" in markdown_lower or "test document" in markdown_lower
    
    print(f"  ✅ Export completed in {export_time*1000:.2f}ms")
    print(f"  ✅ Exported {data['total_blocks']} blocks")
    print(f"  ✅ Markdown length: {len(markdown)} characters")
    
    return markdown

def test_performance_endpoints():
    """Test performance monitoring endpoints."""
    print("🔍 Testing performance endpoints...")
    
    # Get metrics
    response = requests.get(f"{API_BASE}/performance/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, dict)
    print(f"  ✅ Retrieved performance metrics for {len(metrics)} operations")
    
    # Clear metrics
    response = requests.post(f"{API_BASE}/performance/clear")
    assert response.status_code == 200
    print("  ✅ Performance logs cleared")

def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Starting integration tests...\n")
    
    try:
        # Test sequence
        test_health()
        document_id = test_document_creation()
        parse_result = test_markdown_parsing(document_id)
        blocks = test_blocks_retrieval(document_id)
        test_block_update(blocks)
        toc = test_toc_generation(document_id)
        exported_markdown = test_markdown_export(document_id)
        test_performance_endpoints()
        
        print("\n🎉 All integration tests passed!")
        print(f"📊 Test Summary:")
        print(f"   - Document ID: {document_id}")
        print(f"   - Total blocks: {parse_result['total_blocks']}")
        print(f"   - ToC entries: {len(toc)}")
        print(f"   - Export size: {len(exported_markdown)} chars")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
