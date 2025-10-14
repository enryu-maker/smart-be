from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocale
from app.model.room import Room
from app.schemas.room_schema import RoomCreate, RoomResponse
from app.service.user_service import decode_access_token

router = APIRouter(
    prefix="/v1/room",
    tags=["V1 ROOM API"],
)


# Dependency
def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(decode_access_token)]


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    db: db_dependency,
    user: user_dependency,
    space_name: str = Form(...),
    space_type: str = Form(None)
):
    """Create a room for the logged-in user"""
    new_room = Room(
        space_name=space_name,
        space_type=space_type,
        user_id=user["user_id"],
        date_added=datetime.utcnow()
    )

    try:
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return new_room
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room: {str(e)}"
        )


@router.get("/", response_model=List[RoomResponse])
async def list_user_rooms(db: db_dependency, user: user_dependency):
    """List all rooms created by the logged-in user"""
    rooms = db.query(Room).filter(Room.user_id == user["user_id"]).all()
    return rooms


@router.delete("/{room_id}/", status_code=status.HTTP_200_OK)
async def delete_room(room_id: int, db: db_dependency, user: user_dependency):
    """Delete a specific room (only if owned by the user)"""
    room = db.query(Room).filter(
        Room.id == room_id, Room.user_id == user["user_id"]).first()

    if not room:
        raise HTTPException(
            status_code=404, detail="Room not found or not yours.")

    db.delete(room)
    db.commit()
    return {"message": "Room deleted successfully."}
