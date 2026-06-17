from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="sessions")
    uploaded_files = relationship("UploadedFile", back_populates="session")
    messages = relationship("Message", back_populates="session")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    session = relationship("Session", back_populates="uploaded_files")
    chunks = relationship("Chunk", back_populates="file")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    file_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_files.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(String)  # Placeholder for pgvector vector type
    row_start = Column(Integer, nullable=False)
    row_end = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    file = relationship("UploadedFile", back_populates="chunks")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    session = relationship("Session", back_populates="messages")