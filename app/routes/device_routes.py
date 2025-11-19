from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Form, Query
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from app.database import SessionLocale
from app.model.room import Device, Room
from app.model.blockchain import DeviceBlock
from app.schemas.device_schema import DeviceCreate, DeviceResponse
from app.service.user_service import decode_access_token
import json

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
    device_name: str = Form(...),
    device_type: str = Form(None),
    room_id: int = Form(...)
):
    """Create a new device under a user's room and add it to the room's blockchain"""
    # Step 1: Verify room ownership
    room = (
        db.query(Room)
        .filter(Room.id == room_id, Room.user_id == user["id"])
        .first()
    )

    if not room:
        raise HTTPException(
            status_code=404, detail="Room not found or not yours.")

    # Step 2: Create new device
    new_device = Device(
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

        # Step 3: Prepare blockchain data
        last_block = (
            db.query(DeviceBlock)
            .filter(DeviceBlock.room_id == room_id)
            .order_by(DeviceBlock.id.desc())
            .first()
        )
        previous_hash = last_block.hash if last_block else None

        data_json = json.dumps({
            "device_name": device_name,
            "device_type": device_type,
            "is_on": new_device.is_on,
            "timestamp": str(datetime.utcnow())
        })

        # Step 4: Create new blockchain block
        block_content = f"{room_id}{new_device.id}{data_json}{previous_hash or ''}"
        current_hash = hashlib.sha256(block_content.encode()).hexdigest()

        new_block = DeviceBlock(
            room_id=room_id,
            device_id=new_device.id,
            data=data_json,
            previous_hash=previous_hash,
            hash=current_hash
        )

        db.add(new_block)
        db.commit()

        return new_device

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create device: {str(e)}"
        )


@router.get("/", response_model=List[DeviceResponse])
async def list_user_devices(
    db: db_dependency,
    user: user_dependency,
    room_id: int = Query(None, description="Filter devices by room_id")
):
    """List all devices belonging to the user's rooms (optionally filter by room_id)."""
    query = (
        db.query(Device)
        .join(Room)
        .filter(Room.user_id == user["id"])
    )

    if room_id is not None:
        query = query.filter(Device.room_id == room_id)

    devices = query.all()
    return devices


@router.patch("/{device_id}/toggle/", response_model=DeviceResponse)
async def toggle_device(device_id: int, db: db_dependency):
    """Public endpoint to toggle ON/OFF for a device (no user authentication)."""
    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found.")

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
        .filter(Device.id == device_id, Room.user_id == user["id"])
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
        .filter(Device.id == device_id, Room.user_id == user["id"])
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
    db: db_dependency
):
    """Public: Check the ON/OFF status of a specific device"""

    device = db.query(Device).filter(Device.id == device_id).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found."
        )

    # Convert device.status → True | False | None
    if device.is_on is True:
        status_value = True
    elif device.is_on is False:
        status_value = False
    else:
        status_value = None

    return status_value
