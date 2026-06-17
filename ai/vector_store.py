import os
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import Json
import numpy as np

class VectorStore:
    """PgVector store for embedding vectors."""
    
    def __init__(self):
        # Lazy initialization
        self._connection = None
        self.dimension = 1536  # From spec
        
    def _ensure_connection(self):
        if self._connection is None:
            conn_string = os.getenv("DATABASE_URL")
            if not conn_string:
                raise ValueError("DATABASE_URL environment variable not set")
            self._connection = psycopg2.connect(conn_string)
            # Enable vector extension
            with self._connection.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                self._connection.commit()
    
    def _create_table_if_not_exists(self):
        """Create the embeddings table if it doesn't exist."""
        self._ensure_connection()
        with self._connection.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id VARCHAR(255) PRIMARY KEY,
                    embedding vector({self.dimension}),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create index for cosine similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx 
                ON embeddings USING ivfflat (embedding vector_cosine_ops)
            """)
            self._connection.commit()
    
    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]):
        """Insert or update a vector with metadata."""
        self._ensure_connection()
        self._create_table_if_not_exists()
        
        # Ensure vector has correct dimension
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} does not match expected {self.dimension}")
        
        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO embeddings (id, embedding, metadata)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = CURRENT_TIMESTAMP
            """, (id, vector, Json(metadata)))
            self._connection.commit()
    
    def search(self, query_embedding: List[float], top_k: int = 5, **filters) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity.
        
        Args:
            query_embedding: The query vector
            top_k: Number of results to return
            **filters: Optional metadata filters (e.g., session_id='abc')
            
        Returns:
            List of matches with id, metadata, and similarity score
        """
        self._ensure_connection()
        
        # Ensure query vector has correct dimension
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query vector dimension {len(query_embedding)} does not match expected {self.dimension}")
        
        # Build WHERE clause for metadata filters
        where_clauses = []
        params = [query_embedding, top_k]
        
        for key, value in filters.items():
            where_clauses.append(f"metadata->>%s = %s")
            params.extend([key, str(value)])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"
        
        query = f"""
            SELECT 
                id,
                metadata,
                1 - (embedding <=> %s) as similarity
            FROM embeddings
            WHERE {where_sql}
            ORDER BY embedding <=> %s
            LIMIT %s
        """
        
        with self._connection.cursor() as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            
        return [
            {
                "id": row[0],
                "metadata": row[1],
                "similarity": float(row[2])
            }
            for row in results
        ]
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None