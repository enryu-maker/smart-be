from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocale
from app.model.room import Device
from app.model.room import Room
from app.schemas.device_schema import DeviceCreate, DeviceResponse
from app.service.user_service import decode_access_token

router = APIRouter(
    prefix="/v1/device",
    tags=["V1 DEVICE API"],
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


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    db: db_dependency,
    user: user_dependency,
    device_id: str = Form(...),
    device_name: str = Form(...),
    device_type: str = Form(None),
    room_id: int = Form(...)
):
    """Create a new device under a user's room"""
    room = db.query(Room).filter(
        Room.id == room_id, Room.user_id == user["user_id"]).first()

    if not room:
        raise HTTPException(
            status_code=404, detail="Room not found or not yours.")

    new_device = Device(
        device_id=device_id,
        device_name=device_name,
        device_type=device_type,
        room_id=room_id,
        date_added=datetime.utcnow(),
        is_on=False
    )

    try:
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create device: {str(e)}"
        )


@router.get("/", response_model=List[DeviceResponse])
async def list_user_devices(db: db_dependency, user: user_dependency):
    """List all devices belonging to the user's rooms"""
    devices = (
        db.query(Device)
        .join(Room)
        .filter(Room.user_id == user["user_id"])
        .all()
    )
    return devices


@router.patch("/{device_id}/toggle/", response_model=DeviceResponse)
async def toggle_device(device_id: int, db: db_dependency, user: user_dependency):
    """Toggle ON/OFF for a device (only if owned by the user)"""
    device = (
        db.query(Device)
        .join(Room)
        .filter(Device.id == device_id, Room.user_id == user["user_id"])
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=404, detail="Device not found or not yours.")

    device.is_on = not device.is_on
    db.commit()
    db.refresh(device)
    return device


@router.get("/{device_id}/", response_model=DeviceResponse, status_code=status.HTTP_200_OK)
async def get_single_device(
    device_id: int,
    db: db_dependency,
    user: user_dependency
):
    """Get details of a single device (only if owned by the logged-in user)."""
    device = (
        db.query(Device)
        .join(Room)
        .filter(Device.id == device_id, Room.user_id == user["user_id"])
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by you."
        )

    return device


@router.delete("/{device_id}/", status_code=status.HTTP_200_OK)
async def delete_device(device_id: int, db: db_dependency, user: user_dependency):
    """Delete device (only if owned by the user)"""
    device = (
        db.query(Device)
        .join(Room)
        .filter(Device.id == device_id, Room.user_id == user["user_id"])
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=404, detail="Device not found or not yours.")

    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully."}


@router.get("/{device_id}/status", status_code=status.HTTP_200_OK)
async def get_device_status(
    device_id: int,
    db: db_dependency,
    user: user_dependency
):
    """Check the status of a specific device (only if owned by the user)"""

    device = (
        db.query(Device)
        .join(Room)
        .filter(Device.id == device_id, Room.user_id == user["user_id"])
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or not yours."
        )

    # Convert device.status → True | False | None
    # Adjust logic based on how your Device model stores status
    if device.status is True:
        status_value = True
    elif device.status is False:
        status_value = False
    else:
        status_value = None

    return {
        "device_id": device.id,
        "status": status_value
    }
