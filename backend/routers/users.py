from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.routers.auth import get_current_user
from database.config import get_db
from database.models import User

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic schemas
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user exists
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user is updating themselves
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    # Check if email is being changed and if it's already taken
    if "email" in update_data and update_data["email"] != user.email:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = update_data["email"]
    
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user exists
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user is deleting themselves
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    db.delete(user)
    db.commit()
    return None