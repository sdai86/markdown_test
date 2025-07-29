# Markdown Editor - Block-Based Editing System

A high-performance full-stack application for editing large Markdown documents with block-based structure, virtualized rendering, and real-time collaboration features.

## 🏗️ Architecture

- **Frontend**: React with TypeScript, virtualized rendering
- **Backend**: FastAPI with Python, block-based Markdown parsing
- **Database**: PostgreSQL with optimized schema
- **Infrastructure**: Docker Compose for local development

## ✨ Features

### Core Functionality
- **Block-based Markdown parsing** - Documents are parsed into individual blocks (headings, paragraphs, code blocks, etc.)
- **Virtualized rendering** - Smooth performance with large documents (1000+ blocks)
- **Real-time inline editing** - Click-to-edit with debounced auto-save
- **Interactive Table of Contents** - Navigate large documents with click-to-scroll
- **Performance optimized** - Initial load < 200ms, updates < 100ms
- **Export functionality** - Reassemble blocks back to Markdown

### Advanced Features
- **AST parsing support** - Optional markdown-it-py integration for rich parsing
- **Performance monitoring** - Built-in metrics and logging
- **Integration testing** - Automated tests for performance requirements
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
# Generate and load sample data
python scripts/generate_sample_data.py
python scripts/load_sample_data.py
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
│   ├── main.py                # API endpoints
│   ├── database.py            # Database models and connection
│   ├── schemas.py             # Pydantic schemas
│   ├── markdown_parser.py     # Block-based parser
│   ├── performance_logger.py  # Performance monitoring
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.tsx           # Main application
│   │   ├── components/       # React components
│   │   └── types.ts          # TypeScript types
│   ├── package.json          # Node dependencies
│   └── Dockerfile           # Frontend container
├── tests/                    # Integration tests
│   └── test_integration.py  # Performance and functionality tests
├── scripts/                 # Utility scripts
│   ├── generate_sample_data.py  # Sample data generator
│   └── load_sample_data.py     # Data loader
└── sample_data/             # Generated sample files
    └── large_sample.md      # Large test document
```

## 🔧 Development

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run locally (requires PostgreSQL)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/markdown_editor"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
# Run all tests
cd tests
python -m pytest test_integration.py -v

# Run specific test
python -m pytest test_integration.py::test_blocks_retrieval_performance -v
```

### Performance Testing
```bash
# Load sample data and run performance tests
python scripts/load_sample_data.py

# Check performance metrics
curl http://localhost:8000/performance/metrics
```

## 📊 API Endpoints

### Documents
- `GET /documents` - List all documents
- `POST /documents` - Create a new document
- `GET /documents/{id}` - Get document details

### Blocks
- `GET /blocks?document_id=...&offset=...&limit=...` - Get paginated blocks
- `GET /blocks/{id}` - Get specific block
- `PATCH /blocks/{id}` - Update block content

### Content Management
- `POST /documents/{id}/parse` - Parse markdown content into blocks
- `GET /toc?document_id=...` - Get table of contents
- `GET /export?document_id=...` - Export blocks to markdown

### Performance Monitoring
- `GET /performance/metrics` - Get performance metrics
- `POST /performance/clear` - Clear metrics

## ⚡ Performance Requirements

The application is designed to meet strict performance requirements:

- **Initial Load**: < 200ms for first 100 blocks
- **Block Updates**: < 100ms for PATCH operations
- **Smooth Scrolling**: No frame drops during virtualized scrolling
- **Memory Efficient**: Handles 1000+ blocks without memory issues

### Performance Features
- Virtualized rendering with react-window
- Debounced auto-save (500ms delay)
- Optimized database queries with proper indexing
- Performance monitoring and logging
- Efficient block-based parsing

## 🎯 Usage Guide

### Loading Documents
1. Start the application with `docker-compose up`
2. Generate sample data with `python scripts/generate_sample_data.py`
3. Load data with `python scripts/load_sample_data.py`
4. Access the frontend at http://localhost:3000

### Editing Content
1. Click on any block to start editing
2. Changes are automatically saved after 500ms
3. Use Ctrl+Enter to save immediately
4. Use Escape to cancel editing

### Navigation
1. Use the Table of Contents sidebar to navigate
2. Click on any heading to scroll to that section
3. The current section is highlighted based on scroll position

### Exporting
1. Use the API endpoint `GET /export?document_id=...` to get markdown
2. The export reassembles all blocks in order
3. Original formatting is preserved where possible

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