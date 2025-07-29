# Markdown Editor - AST-Based Document System

A high-performance full-stack application for editing large Markdown documents (300+ pages) with AST-based architecture, virtualized rendering, and scalable document management designed for millions of documents.

## 🏗️ Architecture

- **Frontend**: React with TypeScript, remark ecosystem for markdown processing
- **Backend**: FastAPI with Python, markdown-it-py for AST parsing
- **Database**: PostgreSQL with JSONB storage for AST documents
- **Infrastructure**: Docker Compose for local development

## ✨ Features

### Core Functionality
- **AST-based document storage** - Documents stored as single JSON AST structures for optimal scalability
- **Virtualized rendering** - Smooth performance with massive documents (40,000+ blocks)
- **Raw markdown editing** - Block-level and full-document raw markdown editing with structural changes
- **Interactive Table of Contents** - Navigate large documents with hierarchical outline (H1, H2, H3)
- **Performance optimized** - Handles 945-page documents with 40,505 blocks efficiently
- **Export functionality** - Markdown and HTML export with proper formatting

### Advanced Features
- **Professional markdown libraries** - remark ecosystem (frontend), markdown-it-py (backend)
- **Rich markdown editor** - @uiw/react-md-editor with WYSIWYG capabilities
- **Scalable architecture** - Designed for millions of 300+ page documents
- **Performance monitoring** - Built-in metrics and logging
- **Integration testing** - Automated tests for large document performance
- **Responsive design** - Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for running scripts)
- Node.js 18+ (for frontend development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd markdown_test
```

### 2. Start the Application
```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose logs -f backend
```

### 3. Load Sample Data
```bash
# Generate large AST-based sample document (945 pages, 40,505 blocks)
python backend/generate_ast_sample.py
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
markdown_test/
├── docker-compose.yml          # Docker orchestration
├── backend/                    # FastAPI backend
│   ├── main_ast.py            # AST-based API endpoints
│   ├── database.py            # Database models and connection
│   ├── schemas.py             # Pydantic schemas for AST documents
│   ├── services/              # Business logic services
│   │   └── document_service.py # AST document operations
│   ├── generate_ast_sample.py # Large sample document generator
│   ├── performance_logger.py  # Performance monitoring
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── AppAST.tsx        # Main AST-based application
│   │   ├── components/       # React components
│   │   │   ├── MarkdownRenderer.tsx # Professional markdown rendering
│   │   │   ├── MarkdownEditor.tsx   # Rich markdown editor
│   │   │   └── RawMarkdownEditor.tsx # Full-document raw editor
│   │   ├── contexts/         # React contexts
│   │   │   └── DocumentContext.tsx # Document state management
│   │   ├── services/         # API services
│   │   │   └── documentService.ts # Document API client
│   │   └── types.ts          # TypeScript types
│   ├── package.json          # Node dependencies (remark ecosystem)
│   └── Dockerfile           # Frontend container
├── scripts/                 # Utility scripts
│   └── test_ast_integration.py # AST integration tests
└── README.md               # This documentation
```

## 🔧 Development

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run locally (requires PostgreSQL)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/markdown_editor"
uvicorn main_ast:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm start
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d markdown_editor

# View logs
docker-compose logs db
```

## 🧪 Testing

### Run Integration Tests
```bash
# Run AST integration tests
python scripts/test_ast_integration.py

# Tests include:
# - Document loading and AST parsing
# - Block virtualization and rendering
# - Table of contents generation
# - Search functionality
# - Export (Markdown and HTML)
# - Performance benchmarks
```

### Performance Testing
```bash
# Generate large sample document and test performance
python backend/generate_ast_sample.py
python scripts/test_ast_integration.py

# Check performance metrics
curl http://localhost:8000/performance/metrics
```

## 📊 API Endpoints

### Documents (AST-based)
- `GET /documents` - List all documents
- `POST /documents` - Create a new document with AST structure
- `GET /documents/{id}` - Get document with full AST
- `PUT /documents/{id}/update-from-markdown` - Update document from raw markdown

### Virtual Blocks (for UI rendering)
- `GET /documents/{id}/blocks?offset=...&limit=...` - Get virtualized blocks from AST
- `PUT /documents/{id}/blocks/{block_index}` - Update specific AST node via block interface

### Content Management
- `GET /documents/{id}/outline` - Get hierarchical table of contents from AST
- `GET /documents/{id}/search?query=...` - Search within document AST
- `GET /documents/{id}/export/markdown` - Export AST to markdown
- `GET /documents/{id}/export/html` - Export AST to HTML

### Performance Monitoring
- `GET /performance/metrics` - Get performance metrics
- `POST /performance/clear` - Clear metrics

## ⚡ Performance Requirements

The application is designed to handle massive documents efficiently:

- **Large Documents**: Supports 300+ page documents (40,000+ blocks)
- **Initial Load**: < 2000ms for massive documents (945 pages)
- **Block Updates**: < 100ms for AST node operations
- **Smooth Scrolling**: No frame drops during virtualized scrolling
- **Memory Efficient**: Handles 40,000+ blocks without memory issues
- **Scalability**: Designed for millions of documents

### Performance Features
- AST-based document storage (single JSONB record vs thousands of block records)
- Virtualized rendering with react-window VariableSizeList
- Professional markdown libraries (remark, markdown-it-py)
- Optimized database queries with GIN indexing on JSONB
- Performance monitoring and logging
- Efficient AST parsing and manipulation

## 🎯 Usage Guide

### Loading Documents
1. Start the application with `docker-compose up -d`
2. Generate large sample document with `python backend/generate_ast_sample.py`
3. Access the frontend at http://localhost:3000
4. The 945-page document with 40,505 blocks will be automatically loaded

### Editing Content
1. **Block-level editing**: Click the edit button (✏️) on any block header
2. **Raw markdown editing**: Edit the raw markdown content with rich editor
3. **Full-document editing**: Use the "Raw Edit" button for entire document editing
4. **Structural changes**: Adding/removing headings automatically updates ToC and hierarchy
5. Changes are automatically saved with AST re-parsing

### Navigation
1. Use the hierarchical Table of Contents sidebar (H1, H2, H3 levels)
2. Click on any heading to scroll to that section
3. The current section is highlighted based on scroll position
4. Search functionality to find content across the document

### Exporting
1. Click the "Export" button in the UI for dropdown menu
2. Choose "📄 Markdown" for markdown export
3. Choose "🌐 HTML" for HTML export
4. Original formatting and structure are preserved

## 🔍 Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check if ports are available
lsof -i :3000 -i :8000 -i :5432

# Restart services
docker-compose down
docker-compose up -d
```

**Database connection errors**
```bash
# Check database status
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

**Frontend build errors**
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Performance issues**
```bash
# Check performance metrics
curl http://localhost:8000/performance/metrics

# Clear metrics
curl -X POST http://localhost:8000/performance/clear
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## 🛠️ Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `REACT_APP_API_URL` - Backend API URL for frontend
- `NODE_ENV` - Environment (development/production)

### Docker Compose Override
Create `docker-compose.override.yml` for local customizations:
```yaml
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=true
  frontend:
    environment:
      - REACT_APP_DEBUG=true
```

## 📈 Monitoring and Metrics

The application includes comprehensive performance monitoring:

### Backend Metrics
- API endpoint response times
- Database query performance
- Markdown parsing duration
- Block update latency

### Frontend Metrics
- Component render times
- Virtualized list performance
- API call durations
- User interaction latency

### Accessing Metrics
```bash
# Get current metrics
curl http://localhost:8000/performance/metrics

# Performance summary
curl http://localhost:8000/performance/metrics | jq '.summary'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Submit a pull request

### Development Guidelines
- Follow TypeScript best practices for frontend
- Use type hints for Python backend code
- Write tests for new features
- Maintain performance requirements
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI, React, and PostgreSQL
- Uses markdown-it-py for AST parsing
- Virtualized rendering with react-window
- Performance monitoring with custom middleware