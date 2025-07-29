-- Initialize the database schema for markdown blocks

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table to store markdown blocks
CREATE TABLE IF NOT EXISTS blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL, -- 'heading', 'paragraph', 'code', 'list', 'blockquote', etc.
    content TEXT NOT NULL,
    raw_content TEXT, -- Original markdown content
    order_index INTEGER NOT NULL,
    level INTEGER DEFAULT 0, -- For headings (1-6), list nesting, etc.
    parent_id UUID REFERENCES blocks(id) ON DELETE CASCADE,
    document_id UUID NOT NULL, -- To support multiple documents
    metadata JSONB DEFAULT '{}', -- Additional metadata (language for code blocks, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table to store document metadata
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255),
    total_blocks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_blocks_document_id ON blocks(document_id);
CREATE INDEX IF NOT EXISTS idx_blocks_order ON blocks(document_id, order_index);
CREATE INDEX IF NOT EXISTS idx_blocks_type ON blocks(type);
CREATE INDEX IF NOT EXISTS idx_blocks_parent ON blocks(parent_id);
CREATE INDEX IF NOT EXISTS idx_blocks_level ON blocks(level);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_blocks_updated_at BEFORE UPDATE ON blocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
