#!/usr/bin/env python3
"""
Script to load sample markdown data into the application.
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

API_BASE_URL = "http://localhost:8000"

def wait_for_api(max_attempts=30, delay=2):
    """Wait for the API to be available."""
    print("Waiting for API to be available...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("API is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - API not ready, waiting {delay}s...")
        time.sleep(delay)
    
    print("API failed to become available")
    return False

def create_document(title: str, filename: str):
    """Create a new document."""
    response = requests.post(f"{API_BASE_URL}/documents", json={
        "title": title,
        "filename": filename
    })
    
    if response.status_code == 200:
        doc = response.json()
        print(f"Created document: {doc['title']} (ID: {doc['id']})")
        return doc['id']
    else:
        print(f"Failed to create document: {response.text}")
        return None

def load_markdown_file(document_id: str, file_path: str, use_ast: bool = False):
    """Load a markdown file into the specified document."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Loading markdown file: {file_path}")
    print(f"File size: {len(content)} characters")
    
    start_time = time.time()
    
    response = requests.post(
        f"{API_BASE_URL}/documents/{document_id}/parse",
        params={
            "use_ast": use_ast
        },
        json={
            "markdown_content": content
        }
    )
    
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"Successfully loaded {result['total_blocks']} blocks in {duration:.2f}s")
        print(f"Parse stats: {result['parse_stats']}")
        return True
    else:
        print(f"Failed to load markdown: {response.text}")
        return False

def test_performance(document_id: str):
    """Test the performance of various operations."""
    print("\n=== Performance Testing ===")
    
    # Test block retrieval
    print("Testing block retrieval (first 100 blocks)...")
    start_time = time.time()
    
    response = requests.get(f"{API_BASE_URL}/blocks", params={
        "document_id": document_id,
        "offset": 0,
        "limit": 100
    })
    
    duration_ms = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        result = response.json()
        print(f"Retrieved {len(result['blocks'])} blocks in {duration_ms:.2f}ms")
        
        if duration_ms < 200:
            print("✅ Meets performance requirement (< 200ms)")
        else:
            print("❌ Does not meet performance requirement (< 200ms)")
    
    # Test ToC generation
    print("\nTesting ToC generation...")
    start_time = time.time()
    
    response = requests.get(f"{API_BASE_URL}/toc", params={
        "document_id": document_id
    })
    
    duration_ms = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        toc = response.json()
        print(f"Generated ToC with {len(toc)} items in {duration_ms:.2f}ms")
    
    # Test block update
    if response.status_code == 200 and len(result['blocks']) > 0:
        print("\nTesting block update...")
        block_id = result['blocks'][0]['id']
        
        start_time = time.time()
        
        update_response = requests.patch(f"{API_BASE_URL}/blocks/{block_id}", json={
            "content": "Updated content for performance test"
        })
        
        duration_ms = (time.time() - start_time) * 1000
        
        if update_response.status_code == 200:
            print(f"Updated block in {duration_ms:.2f}ms")
            
            if duration_ms < 100:
                print("✅ Meets performance requirement (< 100ms)")
            else:
                print("❌ Does not meet performance requirement (< 100ms)")

def main():
    """Main function to load sample data."""
    print("=== Markdown Editor Sample Data Loader ===")
    
    # Wait for API
    if not wait_for_api():
        sys.exit(1)
    
    # Generate sample data if it doesn't exist
    sample_file = Path(__file__).parent.parent / "sample_data" / "large_sample.md"
    
    if not sample_file.exists():
        print("Sample file not found, generating...")
        generate_script = Path(__file__).parent / "generate_sample_data.py"
        os.system(f"python {generate_script}")
    
    # Create document
    document_id = create_document(
        title="Large Sample Document",
        filename="large_sample.md"
    )
    
    if not document_id:
        sys.exit(1)
    
    # Load markdown file
    success = load_markdown_file(document_id, str(sample_file))
    
    if success:
        # Test performance
        test_performance(document_id)
        
        print(f"\n=== Sample Data Loaded Successfully ===")
        print(f"Document ID: {document_id}")
        print(f"You can now access the application at http://localhost:3000")
        print(f"API documentation at http://localhost:8000/docs")
    else:
        print("Failed to load sample data")
        sys.exit(1)

if __name__ == "__main__":
    main()
