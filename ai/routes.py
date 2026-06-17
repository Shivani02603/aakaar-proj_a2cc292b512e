from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import logging
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ai.ingest import ingest_excel_file
from ai.rag import answer_question

router = APIRouter(prefix='/api/ai', tags=['AI'])
logger = logging.getLogger(__name__)

class IngestRequest(BaseModel):
    session_id: str = Field(..., description="ID of the session to link the file to")
    filename: str = Field(..., description="Original filename")

class IngestResponse(BaseModel):
    file_id: str
    filename: str
    session_id: str
    chunk_count: int
    ingested_at: datetime

class QueryRequest(BaseModel):
    session_id: str = Field(..., description="ID of the session to query within")
    question: str = Field(..., description="Natural language question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")

class SourceCitation(BaseModel):
    file_id: str
    filename: str
    chunk_id: str
    content_preview: str
    start_row: int
    end_row: int

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    session_id: str
    question: str
    generated_at: datetime

@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    session_id: str,
    filename: str,
    file: UploadFile = File(...)
):
    """
    Ingest an Excel file for a given session.
    """
    try:
        if not filename.lower().endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
        
        logger.info(f"Ingesting file {filename} for session {session_id}")
        
        file_id = str(uuid.uuid4())
        
        chunk_count = await ingest_excel_file(
            file_id=file_id,
            session_id=session_id,
            filename=filename,
            file_content=await file.read()
        )
        
        return IngestResponse(
            file_id=file_id,
            filename=filename,
            session_id=session_id,
            chunk_count=chunk_count,
            ingested_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest
):
    """
    Answer a question using RAG on ingested files in the session.
    """
    try:
        logger.info(f"Processing query for session {request.session_id}: {request.question[:100]}...")
        
        answer, sources = await answer_question(
            session_id=request.session_id,
            question=request.question,
            top_k=request.top_k
        )
        
        source_citations = []
        for source in sources:
            source_citations.append(SourceCitation(
                file_id=source.get('file_id', ''),
                filename=source.get('filename', ''),
                chunk_id=source.get('chunk_id', ''),
                content_preview=source.get('content_preview', '')[:200],
                start_row=source.get('start_row', 0),
                end_row=source.get('end_row', 0)
            ))
        
        return QueryResponse(
            answer=answer,
            sources=source_citations,
            session_id=request.session_id,
            question=request.question,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to process query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")