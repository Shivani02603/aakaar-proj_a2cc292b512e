import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

# Add the parent directory to the path so we can import from database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, User, Session, UploadedFile, Chunk, Message, SessionLocal, engine
from sqlalchemy.orm import Session as DBSessionType


def seed_database():
    """Seed the database with realistic sample data."""
    session: DBSessionType = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        # Clear existing data (optional, for clean seeding)
        # Note: This will delete all existing data in the tables
        print("Clearing existing data...")
        session.query(Message).delete()
        session.query(Chunk).delete()
        session.query(UploadedFile).delete()
        session.query(Session).delete()
        session.query(User).delete()
        session.commit()
        
        # Create Users (parent table)
        print("Creating users...")
        users = [
            User(
                id=uuid4(),
                email="alice.johnson@example.com",
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            User(
                id=uuid4(),
                email="bob.smith@example.com",
                created_at=datetime.utcnow() - timedelta(days=25)
            ),
            User(
                id=uuid4(),
                email="carol.williams@example.com",
                created_at=datetime.utcnow() - timedelta(days=15)
            )
        ]
        
        for user in users:
            session.add(user)
        session.flush()  # Assign IDs without committing
        
        # Create Sessions (child of Users)
        print("Creating sessions...")
        sessions = [
            Session(
                id=uuid4(),
                user_id=users[0].id,
                name="Quarterly Financial Analysis",
                created_at=datetime.utcnow() - timedelta(days=10)
            ),
            Session(
                id=uuid4(),
                user_id=users[0].id,
                name="Market Research Project",
                created_at=datetime.utcnow() - timedelta(days=5)
            ),
            Session(
                id=uuid4(),
                user_id=users[1].id,
                name="Technical Documentation Review",
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            Session(
                id=uuid4(),
                user_id=users[2].id,
                name="Competitive Analysis",
                created_at=datetime.utcnow() - timedelta(days=1)
            )
        ]
        
        for session_obj in sessions:
            session.add(session_obj)
        session.flush()
        
        # Create UploadedFiles (child of Sessions)
        print("Creating uploaded files...")
        uploaded_files = [
            UploadedFile(
                id=uuid4(),
                session_id=sessions[0].id,
                filename="Q4_2023_earnings.pdf",
                file_path="/uploads/Q4_2023_earnings.pdf",
                uploaded_at=datetime.utcnow() - timedelta(days=9, hours=2)
            ),
            UploadedFile(
                id=uuid4(),
                session_id=sessions[0].id,
                filename="financial_metrics.xlsx",
                file_path="/uploads/financial_metrics.xlsx",
                uploaded_at=datetime.utcnow() - timedelta(days=9, hours=1)
            ),
            UploadedFile(
                id=uuid4(),
                session_id=sessions[1].id,
                filename="market_trends_report.pdf",
                file_path="/uploads/market_trends_report.pdf",
                uploaded_at=datetime.utcnow() - timedelta(days=4, hours=3)
            ),
            UploadedFile(
                id=uuid4(),
                session_id=sessions[2].id,
                filename="api_documentation.md",
                file_path="/uploads/api_documentation.md",
                uploaded_at=datetime.utcnow() - timedelta(days=2, hours=5)
            )
        ]
        
        for file in uploaded_files:
            session.add(file)
        session.flush()
        
        # Create Chunks (child of UploadedFiles)
        print("Creating chunks...")
        chunks = [
            # Chunks for Q4_2023_earnings.pdf
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[0].id,
                content="Q4 2023 Earnings Report: Revenue increased by 15% year-over-year to $5.2 billion. Net income reached $1.1 billion, representing a 22% increase compared to Q4 2022.",
                embedding=None,  # In real scenario, this would contain vector embeddings
                row_start=1,
                row_end=3,
                chunk_index=0
            ),
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[0].id,
                content="Operating expenses were $3.4 billion, up 8% from the previous year. The increase was primarily driven by investments in research and development and marketing initiatives.",
                embedding=None,
                row_start=4,
                row_end=6,
                chunk_index=1
            ),
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[0].id,
                content="International markets showed strong growth, with European revenue increasing by 25% and Asian markets growing by 18%. The company expects continued expansion in these regions.",
                embedding=None,
                row_start=7,
                row_end=9,
                chunk_index=2
            ),
            # Chunks for financial_metrics.xlsx
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[1].id,
                content="Key Financial Metrics: Gross margin: 42.5%, Operating margin: 21.8%, Net profit margin: 18.5%. These metrics show improvement across all categories compared to last quarter.",
                embedding=None,
                row_start=1,
                row_end=3,
                chunk_index=0
            ),
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[1].id,
                content="Cash flow from operations: $850 million. Free cash flow: $620 million. The company maintains a strong cash position with $3.2 billion in reserves.",
                embedding=None,
                row_start=4,
                row_end=6,
                chunk_index=1
            ),
            # Chunks for market_trends_report.pdf
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[2].id,
                content="Market Trends Analysis: The AI sector is expected to grow at a CAGR of 35% over the next five years. Cloud computing adoption continues to accelerate across all industries.",
                embedding=None,
                row_start=1,
                row_end=3,
                chunk_index=0
            ),
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[2].id,
                content="Consumer preferences are shifting towards sustainable products, with 68% of surveyed customers willing to pay a premium for environmentally friendly options.",
                embedding=None,
                row_start=4,
                row_end=6,
                chunk_index=1
            ),
            # Chunks for api_documentation.md
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[3].id,
                content="API Documentation: The REST API uses JSON for request and response formats. All endpoints require authentication via API key in the header.",
                embedding=None,
                row_start=1,
                row_end=3,
                chunk_index=0
            ),
            Chunk(
                id=uuid4(),
                file_id=uploaded_files[3].id,
                content="Rate limiting: 100 requests per minute per API key. Response codes: 200 for success, 400 for bad request, 401 for unauthorized, 500 for server errors.",
                embedding=None,
                row_start=4,
                row_end=6,
                chunk_index=1
            )
        ]
        
        for chunk in chunks:
            session.add(chunk)
        session.flush()
        
        # Create Messages (child of Sessions)
        print("Creating messages...")
        messages = [
            # Messages for Quarterly Financial Analysis session
            Message(
                id=uuid4(),
                session_id=sessions[0].id,
                role="user",
                content="What were the key financial highlights from Q4 2023?",
                citations=None,
                created_at=datetime.utcnow() - timedelta(days=9, hours=1, minutes=30)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[0].id,
                role="assistant",
                content="Based on the Q4 2023 earnings report, revenue increased by 15% year-over-year to $5.2 billion, and net income reached $1.1 billion, representing a 22% increase compared to Q4 2022.",
                citations=[{"chunk_id": str(chunks[0].id), "file_name": "Q4_2023_earnings.pdf", "page": 1}],
                created_at=datetime.utcnow() - timedelta(days=9, hours=1, minutes=31)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[0].id,
                role="user",
                content="How did international markets perform?",
                citations=None,
                created_at=datetime.utcnow() - timedelta(days=9, hours=1, minutes=35)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[0].id,
                role="assistant",
                content="International markets showed strong growth, with European revenue increasing by 25% and Asian markets growing by 18%.",
                citations=[{"chunk_id": str(chunks[2].id), "file_name": "Q4_2023_earnings.pdf", "page": 3}],
                created_at=datetime.utcnow() - timedelta(days=9, hours=1, minutes=36)
            ),
            # Messages for Market Research Project session
            Message(
                id=uuid4(),
                session_id=sessions[1].id,
                role="user",
                content="What are the current market trends in the AI sector?",
                citations=None,
                created_at=datetime.utcnow() - timedelta(days=4, hours=2)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[1].id,
                role="assistant",
                content="The AI sector is expected to grow at a CAGR of 35% over the next five years according to recent market analysis.",
                citations=[{"chunk_id": str(chunks[5].id), "file_name": "market_trends_report.pdf", "page": 1}],
                created_at=datetime.utcnow() - timedelta(days=4, hours=2, minutes=1)
            ),
            # Messages for Technical Documentation Review session
            Message(
                id=uuid4(),
                session_id=sessions[2].id,
                role="user",
                content="What authentication method does the API use?",
                citations=None,
                created_at=datetime.utcnow() - timedelta(days=2, hours=4)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[2].id,
                role="assistant",
                content="The REST API requires authentication via API key in the header for all endpoints.",
                citations=[{"chunk_id": str(chunks[7].id), "file_name": "api_documentation.md", "page": 1}],
                created_at=datetime.utcnow() - timedelta(days=2, hours=4, minutes=1)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[2].id,
                role="user",
                content="What is the rate limit?",
                citations=None,
                created_at=datetime.utcnow() - timedelta(days=2, hours=4, minutes=3)
            ),
            Message(
                id=uuid4(),
                session_id=sessions[2].id,
                role="assistant",
                content="The API has a rate limit of 100 requests per minute per API key.",
                citations=[{"chunk_id": str(chunks[8].id), "file_name": "api_documentation.md", "page": 2}],
                created_at=datetime.utcnow() - timedelta(days=2, hours=4, minutes=4)
            )
        ]
        
        for message in messages:
            session.add(message)
        
        # Commit all changes
        session.commit()
        print("Database seeding completed successfully!")
        
        # Print summary
        print(f"\nSeeding Summary:")
        print(f"- Users created: {len(users)}")
        print(f"- Sessions created: {len(sessions)}")
        print(f"- Uploaded files created: {len(uploaded_files)}")
        print(f"- Chunks created: {len(chunks)}")
        print(f"- Messages created: {len(messages)}")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    seed_database()