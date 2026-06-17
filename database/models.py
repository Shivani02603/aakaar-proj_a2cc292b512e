import os
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session as DBSession

# Use environment variable for database URL
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rag_db")

# Create engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    uploaded_files = relationship("UploadedFile", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, name={self.name}, user_id={self.user_id})>"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="uploaded_files")
    chunks = relationship("Chunk", back_populates="file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename={self.filename}, session_id={self.session_id})>"


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column("embedding", type_=text("vector(1536)"))  # pgvector column for text-embedding-3-small
    row_start = Column(Integer, nullable=False)
    row_end = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)

    # Relationships
    file = relationship("UploadedFile", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk(id={self.id}, file_id={self.file_id}, chunk_index={self.chunk_index})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    citations = Column(JSONB, nullable=True)  # Store source citations as JSON
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


# Define indexes for performance
Index("idx_users_email", User.email, unique=True)
Index("idx_sessions_user_id", Session.user_id)
Index("idx_sessions_created_at", Session.created_at)
Index("idx_uploaded_files_session_id", UploadedFile.session_id)
Index("idx_uploaded_files_uploaded_at", UploadedFile.uploaded_at)
Index("idx_chunks_file_id", Chunk.file_id)
Index("idx_chunks_chunk_index", Chunk.chunk_index)
Index("idx_messages_session_id", Message.session_id)
Index("idx_messages_created_at", Message.created_at)
# Vector similarity index (pgvector)
Index("idx_chunks_embedding", Chunk.embedding, postgresql_using="ivfflat", postgresql_with={"lists": 100})