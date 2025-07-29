
Generate a full-stack local development project with the following architecture and functionality:

🔹 Architecture:
- Frontend: React (Node.js, TypeScript)
- Backend: Python (FastAPI)
- Database: PostgreSQL
- Use Docker Compose to run all services together

🔹 Core Functionality:
- Load and parse a large Markdown file (~300+ pages)
- Backend should:
  - Parse the Markdown into a **block-based structure**
    - Each block is a heading, paragraph, code block, etc.
  - Extract a structured **Table of Contents** (ToC) based on heading hierarchy
  - Optionally support a **Markdown AST mode**:
    - Try parsing Markdown into a full AST (e.g., using `markdown-it-py` or `mistune`)
    - Allow switching between direct block parsing and AST-backed representation

- Store blocks in PostgreSQL using a normalized schema (1 row = 1 block)
- Provide RESTful backend APIs:
  - `GET /blocks?offset=...&limit=...` → paginated block retrieval
  - `GET /toc` → return structured ToC (id, text, level)
  - `PATCH /blocks/{id}` → update a specific block
  - `GET /export` → return a Markdown string reassembled from the stored blocks

🔹 Frontend Functionality:
- Use React with TypeScript
- Display a **virtualized block list** using `react-window` or `react-virtual` to ensure fast rendering
- Render a **sidebar ToC** from the heading structure
- Allow **inline editing** of blocks (heading, paragraph, code) via custom React components
- Click-to-edit → debounce → PATCH to backend
- Click TOC → scroll to block
- Highlight current visible section based on scroll position

🔹 Performance Constraints:
- Initial load (first 100 blocks) must complete in < 200ms
- Updates (PATCH) should respond in < 100ms
- UI must remain smooth during scroll and edits (no full re-renders)

🔹 Testing & Logging:
- Add automated integration tests to verify:
  - Large Markdown document is correctly parsed and inserted
  - TOC is accurate
  - Rendering + scroll work
  - Edits update backend correctly

- Log the following timing information:
  - Initial Markdown parsing time
  - AST-to-block transformation time (if applicable)
  - Block retrieval latency
  - Block update latency
  - Frontend render duration per block (optional)
  - Total Markdown recompile time (on export)

🔹 Optional Enhancements:
- Backend:
  - Implement AST parsing via `markdown-it-py` or `mistune`
  - Allow AST traversal to support:
    - Structured block relationships
    - Rich ToC with anchors
  - Store parsed AST as JSON column for later optimization

- Frontend:
  - Support editing rich content blocks using Editor.js or custom components
  - Use `react-markdown` + plugins for non-editable rendering fallback
  - Track dirty blocks and only send changed ones

🔹 Deliverables:
- `docker-compose.yml` to orchestrate:
  - `frontend` service (React dev server)
  - `backend` service (FastAPI + DB connector)
  - `db` service (PostgreSQL)

- `frontend/`: React app with ToC + virtualized editor
- `backend/`: FastAPI app with parsing, persistence, and export endpoints
- `tests/`: Integration tests with performance logging
- `scripts/`: Initial loader for the 300+ page Markdown file

Include:
- A README with clear instructions
- Seed Markdown test file (~300 pages or ~1,000+ blocks)
- Logging utilities to help evaluate performance across both UI and backend