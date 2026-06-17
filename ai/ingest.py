import os
import pandas as pd
from typing import List, Dict, Any, Tuple
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy imports inside functions to avoid import-time API key issues
def _import_embedding():
    from .embeddings import get_embedding
    return get_embedding

def _import_vector_store():
    from .vector_store import VectorStore
    return VectorStore

def _import_chunker():
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter

def chunk(document: str) -> List[str]:
    """
    Split document into chunks using recursive strategy.
    
    Args:
        document: Text content to chunk
        
    Returns:
        List of text chunks
    """
    try:
        RecursiveCharacterTextSplitter = _import_chunker()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(document)
        return chunks
    except Exception as e:
        logger.error(f"Error in chunking: {e}")
        raise

def _sheet_to_text(df: pd.DataFrame, sheet_name: str) -> str:
    """
    Convert a pandas DataFrame to structured text representation.
    
    Args:
        df: DataFrame to convert
        sheet_name: Name of the Excel sheet
        
    Returns:
        Structured text representation
    """
    lines = []
    lines.append(f"=== Sheet: {sheet_name} ===")
    lines.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    lines.append("")
    
    # Add column names
    lines.append("Columns: " + ", ".join([str(col) for col in df.columns]))
    lines.append("")
    
    # Add sample data (first 50 rows)
    lines.append("Data:")
    for idx, row in df.head(50).iterrows():
        row_data = []
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                value = "[NULL]"
            row_data.append(f"{col}: {value}")
        lines.append(f"Row {idx}: " + " | ".join(row_data))
    
    # If there are more rows, indicate truncation
    if len(df) > 50:
        lines.append(f"... and {len(df) - 50} more rows")
    
    return "\n".join(lines)

def ingest_excel(file_path: str, session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Ingest an Excel file: parse sheets, chunk content, embed, and store vectors.
    
    Args:
        file_path: Path to the Excel file
        session_id: ID of the chat session
        user_id: ID of the user
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        # Read API keys lazily
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Import required modules
        get_embedding = _import_embedding()
        VectorStore = _import_vector_store()
        
        # Read Excel file
        logger.info(f"Reading Excel file: {file_path}")
        excel_file = pd.ExcelFile(file_path)
        
        # Extract filename
        filename = os.path.basename(file_path)
        
        # Initialize vector store
        vector_store = VectorStore()
        
        # Track results
        total_chunks = 0
        sheet_results = []
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            try:
                logger.info(f"Processing sheet: {sheet_name}")
                
                # Read sheet
                df = excel_file.parse(sheet_name)
                
                # Convert sheet to text
                sheet_text = _sheet_to_text(df, sheet_name)
                
                # Chunk the text
                chunks = chunk(sheet_text)
                
                # Process each chunk
                chunk_embeddings = []
                chunk_metadata_list = []
                
                for i, chunk_text in enumerate(chunks):
                    # Generate embedding
                    embedding = get_embedding(chunk_text)
                    
                    # Create metadata
                    chunk_id = str(uuid.uuid4())
                    metadata = {
                        "chunk_id": chunk_id,
                        "filename": filename,
                        "sheet_name": sheet_name,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "session_id": session_id,
                        "user_id": user_id,
                        "row_start": i * (1000 - 200),  # Approximate row range
                        "row_end": min((i + 1) * (1000 - 200), len(df)),
                        "ingested_at": datetime.utcnow().isoformat()
                    }
                    
                    chunk_embeddings.append(embedding)
                    chunk_metadata_list.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": metadata
                    })
                
                # Store embeddings in vector store
                if chunk_embeddings:
                    vector_store.upsert_embeddings(
                        embeddings=chunk_embeddings,
                        metadatas=chunk_metadata_list
                    )
                    total_chunks += len(chunks)
                    
                    sheet_results.append({
                        "sheet_name": sheet_name,
                        "rows": len(df),
                        "columns": len(df.columns),
                        "chunks": len(chunks),
                        "status": "success"
                    })
                    
                    logger.info(f"Sheet '{sheet_name}': {len(chunks)} chunks processed")
                
            except Exception as e:
                logger.error(f"Error processing sheet '{sheet_name}': {e}")
                sheet_results.append({
                    "sheet_name": sheet_name,
                    "status": "error",
                    "error": str(e)
                })
        
        # Store file metadata in database
        try:
            from app.database import get_db
            from app.models import UploadedFile
            
            db = next(get_db())
            uploaded_file = UploadedFile(
                id=str(uuid.uuid4()),
                filename=filename,
                file_path=file_path,
                session_id=session_id,
                user_id=user_id,
                total_chunks=total_chunks,
                sheet_count=len(excel_file.sheet_names),
                ingested_at=datetime.utcnow()
            )
            db.add(uploaded_file)
            db.commit()
            db.refresh(uploaded_file)
            
            logger.info(f"File metadata stored: {uploaded_file.id}")
            
        except Exception as e:
            logger.warning(f"Could not store file metadata in database: {e}")
        
        return {
            "status": "success",
            "filename": filename,
            "total_sheets": len(excel_file.sheet_names),
            "total_chunks": total_chunks,
            "sheet_results": sheet_results,
            "session_id": session_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error ingesting Excel file: {e}")
        return {
            "status": "error",
            "error": str(e),
            "filename": os.path.basename(file_path) if file_path else "unknown",
            "session_id": session_id,
            "user_id": user_id
        }