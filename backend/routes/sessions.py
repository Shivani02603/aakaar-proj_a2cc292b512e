from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.models import Session as DBSession, User
from database.config import get_db

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

class SessionBase(BaseModel):
    user_id: UUID
    name: str

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: UUID
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == session_data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_session = DBSession(user_id=session_data.user_id, name=session_data.name)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return SessionResponse(
        id=db_session.id,
        user_id=db_session.user_id,
        name=db_session.name,
        created_at=db_session.created_at.isoformat()
    )

@router.get("/", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(DBSession).all()
    return [
        SessionResponse(
            id=session.id,
            user_id=session.user_id,
            name=session.name,
            created_at=session.created_at.isoformat()
        )
        for session in sessions
    ]

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        name=session.name,
        created_at=session.created_at.isoformat()
    )