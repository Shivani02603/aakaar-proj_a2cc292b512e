import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.models import UploadedFile, Session as DBSession
from database.config import get_db

router = APIRouter(prefix="/api/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadedFileResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    filename: str
    file_path: str
    uploaded_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=UploadedFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(session_id: uuid.UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    file_id = uuid.uuid4()
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    db_file = UploadedFile(
        id=file_id,
        session_id=session_id,
        filename=file.filename,
        file_path=file_path,
        uploaded_at=datetime.utcnow()
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return UploadedFileResponse(
        id=db_file.id,
        session_id=db_file.session_id,
        filename=db_file.filename,
        file_path=db_file.file_path,
        uploaded_at=db_file.uploaded_at.isoformat()
    )