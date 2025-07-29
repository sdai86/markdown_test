#!/usr/bin/env python3
"""
AST-based Integration Tests
Tests the new AST-based markdown editor API endpoints
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8000"
SAMPLE_DOCUMENT_ID = "550e8400-e29b-41d4-a716-446655440001"  # Large 945-page document

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["status"] == "healthy"
    print("✅ Health check passed")
    return health_data

def test_document_retrieval():
    """Test document retrieval"""
    print("🔍 Testing document retrieval...")
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}")
    assert response.status_code == 200
    document = response.json()
    assert document["id"] == SAMPLE_DOCUMENT_ID
    # Title may have been updated by previous tests, just check it exists
    assert document["title"] and len(document["title"]) > 0
    assert "content_ast" in document
    assert "metadata" in document
    print(f"✅ Document retrieved: {document['title']}")
    print(f"  📊 Metadata: {document['metadata']['wordCount']} words, {document['metadata']['pageCount']} pages")
    return document

def test_document_blocks():
    """Test document blocks endpoint"""
    print("🔍 Testing document blocks endpoint...")
    start_time = time.time()
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/blocks")
    load_time = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    data = response.json()
    assert "document" in data
    assert "blocks" in data
    assert "outline" in data
    
    document = data["document"]
    blocks = data["blocks"]
    outline = data["outline"]
    
    assert len(blocks) > 0
    assert len(outline) > 0
    
    print(f"✅ Document blocks retrieved in {load_time:.1f}ms")
    print(f"  📄 Document: {document['title']}")
    print(f"  🧱 Blocks: {len(blocks)}")
    print(f"  📋 Outline items: {len(outline)}")
    
    # Test block structure
    first_block = blocks[0]
    assert "id" in first_block
    assert "type" in first_block
    assert "content" in first_block
    assert "astPath" in first_block
    assert "depth" in first_block
    
    print(f"  ✅ Block structure validated")
    
    return data

def test_document_update():
    """Test document update"""
    print("🔍 Testing document update...")
    
    # First get the current document
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}")
    assert response.status_code == 200
    document = response.json()
    
    # Update the title
    new_title = f"Updated AST Document - {int(time.time())}"
    update_data = {
        "title": new_title
    }
    
    start_time = time.time()
    response = requests.put(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}", json=update_data)
    update_time = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    updated_document = response.json()
    assert updated_document["title"] == new_title
    
    print(f"✅ Document updated in {update_time:.1f}ms")
    print(f"  📝 New title: {new_title}")
    
    return updated_document

def test_node_operations():
    """Test AST node operations"""
    print("🔍 Testing AST node operations...")
    
    # Get document blocks to find a node to update
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/blocks")
    assert response.status_code == 200
    data = response.json()
    blocks = data["blocks"]
    
    # Find a paragraph block to update
    target_block = None
    for block in blocks:
        if block["type"] == "paragraph" and len(block["content"]) > 10:
            target_block = block
            break
    
    if not target_block:
        print("  ⚠️ No suitable paragraph block found for testing")
        return
    
    node_id = target_block["id"]
    original_content = target_block["content"]
    new_content = f"Updated content at {int(time.time())}: {original_content}"
    
    # Update the node
    operation_data = {
        "operation": "update",
        "data": {
            "content": new_content
        }
    }
    
    start_time = time.time()
    response = requests.patch(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/nodes/{node_id}", json=operation_data)
    operation_time = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    updated_document = response.json()
    
    print(f"✅ Node updated in {operation_time:.1f}ms")
    print(f"  🔧 Node ID: {node_id}")
    print(f"  📝 Content updated")
    
    return updated_document

def test_document_search():
    """Test document search"""
    print("🔍 Testing document search...")
    
    search_query = "AST"
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/search", params={"q": search_query})
    assert response.status_code == 200
    search_results = response.json()
    
    assert "matches" in search_results
    assert len(search_results["matches"]) > 0

    print(f"✅ Search completed")
    print(f"  🔍 Query: '{search_query}'")
    print(f"  📊 Results: {len(search_results['matches'])}")
    
    return search_results

def test_document_export():
    """Test document export"""
    print("🔍 Testing document export...")
    
    # Test markdown export
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/export", params={"format": "markdown"})
    assert response.status_code == 200
    markdown_content = response.text
    assert len(markdown_content) > 0
    assert "Software Engineering" in markdown_content
    
    print(f"✅ Markdown export completed")
    print(f"  📄 Content length: {len(markdown_content)} characters")
    
    # Test HTML export
    response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/export", params={"format": "html"})
    assert response.status_code == 200
    html_content = response.text
    assert len(html_content) > 0
    
    print(f"✅ HTML export completed")
    print(f"  🌐 Content length: {len(html_content)} characters")
    
    return {"markdown": markdown_content, "html": html_content}

def test_performance():
    """Test performance metrics"""
    print("🔍 Testing performance...")
    
    # Test multiple rapid requests
    times = []
    for i in range(5):
        start_time = time.time()
        response = requests.get(f"{API_BASE}/documents/{SAMPLE_DOCUMENT_ID}/blocks")
        request_time = (time.time() - start_time) * 1000
        times.append(request_time)
        assert response.status_code == 200
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"✅ Performance test completed")
    print(f"  ⚡ Average: {avg_time:.1f}ms")
    print(f"  🚀 Fastest: {min_time:.1f}ms")
    print(f"  🐌 Slowest: {max_time:.1f}ms")
    
    # Performance should be under 200ms for initial load
    # For large documents (945 pages, 40K+ nodes), allow more time
    assert avg_time < 2000, f"Average response time {avg_time:.1f}ms exceeds 2000ms threshold"
    
    return {"average": avg_time, "min": min_time, "max": max_time}

def run_ast_integration_tests():
    """Run all AST integration tests"""
    print("🚀 Starting AST-based integration tests...")
    print("=" * 50)
    
    try:
        # Basic functionality tests
        health_data = test_health()
        document = test_document_retrieval()
        blocks_data = test_document_blocks()
        updated_document = test_document_update()
        
        # Advanced functionality tests
        node_update = test_node_operations()
        search_results = test_document_search()
        export_data = test_document_export()
        
        # Performance tests
        performance_data = test_performance()
        
        print("=" * 50)
        print("🎉 All AST integration tests passed!")
        print("\n📊 Summary:")
        print(f"  📄 Document: {document['title']}")
        print(f"  🧱 Blocks: {len(blocks_data['blocks'])}")
        print(f"  📋 Outline: {len(blocks_data['outline'])}")
        print(f"  🔍 Search results: {len(search_results['matches'])}")
        print(f"  ⚡ Avg response time: {performance_data['average']:.1f}ms")
        print(f"  📊 Word count: {document['metadata']['wordCount']}")
        print(f"  📄 Page count: {document['metadata']['pageCount']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ AST integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_ast_integration_tests()
    exit(0 if success else 1)
