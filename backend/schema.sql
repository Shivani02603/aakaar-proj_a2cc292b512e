-- PostgreSQL DDL with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chunks (
    id UUID PRIMARY KEY,
    file_id UUID NOT NULL REFERENCES uploaded_files(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536), -- Adjust dimension as needed
    row_start INTEGER NOT NULL,
    row_end INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    citations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_uploaded_files_session_id ON uploaded_files(session_id);
CREATE INDEX idx_chunks_file_id ON chunks(file_id);
CREATE INDEX idx_messages_session_id ON messages(session_id);