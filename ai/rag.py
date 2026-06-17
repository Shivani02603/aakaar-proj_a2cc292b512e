import os
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

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

def _import_google_genai():
    import google.generativeai as genai
    return genai

def retrieve_context(query: str, top_k: int = 5, session_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context for a query using vector similarity search.
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve
        session_id: Optional session ID filter
        user_id: Optional user ID filter
        
    Returns:
        List of dictionaries with chunk text and metadata
    """
    try:
        # Read API key lazily
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Import required modules
        get_embedding = _import_embedding()
        VectorStore = _import_vector_store()
        
        # Generate query embedding
        query_embedding = get_embedding(query)
        
        # Initialize vector store
        vector_store = VectorStore()
        
        # Search for similar chunks
        search_results = vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            session_id=session_id,
            user_id=user_id
        )
        
        # Format results
        context_chunks = []
        for result in search_results:
            chunk_data = {
                "text": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "score": result.get("score", 0.0)
            }
            context_chunks.append(chunk_data)
        
        logger.info(f"Retrieved {len(context_chunks)} context chunks for query")
        return context_chunks
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        raise

def _build_prompt(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for the Gemini model with context and query.
    
    Args:
        query: User's question
        context_chunks: Retrieved context chunks
        
    Returns:
        Formatted prompt string
    """
    prompt_parts = []
    
    # System instruction
    prompt_parts.append("""You are a helpful data analysis assistant. You answer questions based on the provided context from Excel files.
Your answers should be accurate, concise, and cite specific sources from the context.
If the context doesn't contain enough information to answer the question, say so clearly.""")

    # Add context
    prompt_parts.append("\n=== CONTEXT FROM EXCEL FILES ===")
    
    for i, chunk in enumerate(context_chunks):
        metadata = chunk.get("metadata", {})
        text = chunk.get("text", "")
        
        source_info = []
        if "filename" in metadata:
            source_info.append(f"File: {metadata['filename']}")
        if "sheet_name" in metadata:
            source_info.append(f"Sheet: {metadata['sheet_name']}")
        if "row_start" in metadata and "row_end" in metadata:
            source_info.append(f"Rows: {metadata['row_start']}-{metadata['row_end']}")
        
        source_str = " | ".join(source_info)
        prompt_parts.append(f"\n[Source {i+1}: {source_str}]")
        prompt_parts.append(text)
    
    # Add query
    prompt_parts.append("\n=== USER QUESTION ===")
    prompt_parts.append(query)
    
    # Add answer format instructions
    prompt_parts.append("\n=== ANSWER FORMAT ===")
    prompt_parts.append("""Provide your answer in the following format:

ANSWER: [Your concise answer here]

SOURCES:
1. [Brief source citation 1]
2. [Brief source citation 2]
...""")
    
    return "\n".join(prompt_parts)

def answer_question(query: str, session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Answer a question using RAG: retrieve context and generate answer with Gemini.
    
    Args:
        query: User's question
        session_id: Chat session ID
        user_id: User ID
        
    Returns:
        Dictionary with answer and sources
    """
    try:
        # Read API keys lazily
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Retrieve relevant context
        context_chunks = retrieve_context(
            query=query,
            top_k=5,
            session_id=session_id,
            user_id=user_id
        )
        
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant data in the uploaded files to answer your question.",
                "sources": [],
                "context_available": False
            }
        
        # Build prompt
        prompt = _build_prompt(query, context_chunks)
        
        # Initialize Gemini
        genai = _import_google_genai()
        genai.configure(api_key=google_api_key)
        
        # Use gemini-2.0-flash model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text.strip()
        
        # Parse answer and sources from response
        answer = ""
        sources = []
        
        # Try to parse structured response
        if "ANSWER:" in response_text and "SOURCES:" in response_text:
            parts = response_text.split("SOURCES:")
            answer_part = parts[0].replace("ANSWER:", "").strip()
            sources_part = parts[1].strip() if len(parts) > 1 else ""
            
            answer = answer_part
            
            # Parse sources
            if sources_part:
                source_lines = sources_part.split("\n")
                for line in source_lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-")):
                        # Remove numbering
                        source_text = line.split(". ", 1)[-1] if ". " in line else line.lstrip("- ").strip()
                        if source_text:
                            sources.append(source_text)
        else:
            # Fallback: use entire response as answer
            answer = response_text
            # Extract sources from context chunks
            for chunk in context_chunks:
                metadata = chunk.get("metadata", {})
                source_parts = []
                if "filename" in metadata:
                    source_parts.append(metadata["filename"])
                if "sheet_name" in metadata:
                    source_parts.append(f"Sheet: {metadata['sheet_name']}")
                if source_parts:
                    sources.append(" | ".join(source_parts))
        
        # Limit sources to top 3
        sources = sources[:3]
        
        # Store message in database
        try:
            from app.database import get_db
            from app.models import Message
            
            db = next(get_db())
            message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                query=query,
                answer=answer,
                sources_json=json.dumps(sources),
                retrieved_chunks=len(context_chunks),
                created_at=datetime.utcnow()
            )
            db.add(message)
            db.commit()
            
            logger.info(f"Message stored: {message.id}")
            
        except Exception as e:
            logger.warning(f"Could not store message in database: {e}")
            # Import uuid here to avoid import-time issues
            import uuid
        
        return {
            "answer": answer,
            "sources": sources,
            "context_available": True,
            "retrieved_chunks": len(context_chunks),
            "session_id": session_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return {
            "answer": f"I encountered an error while processing your question: {str(e)}",
            "sources": [],
            "context_available": False,
            "error": str(e)
        }