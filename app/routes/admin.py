from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.model.room import Room, Device
from app.model.user import User


from app.database import SessionLocale
from app.model.admin import Admin
from app.schemas.admin import AdminRegister, AdminLogin, AdminResponse
from app.schemas.room_schema import RoomResponse
from app.schemas.device_schema import DeviceResponse
from app.schemas.user import UserResponse

from app.service.user_service import (
    create_accesss_token,
    decode_access_token,
    hash_password,
    verify_password
)

router = APIRouter(
    prefix="/v1/admin",
    tags=["V1 ADMIN API"],
)

# DB Dependency


def get_db():
    db = SessionLocale()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
admin_dependency = Annotated[dict, Depends(decode_access_token)]


@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def admin_signup(admin: AdminRegister, db: db_dependency):

    existing = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin with this email already exists."
        )

    new_admin = Admin(
        name=admin.name,
        email=admin.email,
        password_hash=hash_password(admin.password),
        is_active=True
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"message": "Admin registered successfully"}


@router.post("/login/")
async def admin_login(login: AdminLogin, db: db_dependency):

    admin = db.query(Admin).filter(Admin.email == login.email).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found."
        )

    if not verify_password(login.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password."
        )

    access_token = create_accesss_token(
        admin.name, admin.id, timedelta(days=90))

    return {
        "message": "Login successful",
        "access_token": access_token
    }

# api for user active status management


@router.put("/toggle-user-status/{user_id}/")
async def admin_toggle_user_status(user_id: int, db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    print(user_id)
    target_user = db.query(User).filter(User.id == user_id).first()
    print(target_user)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    target_user.is_active = not target_user.is_active
    db.commit()
    db.refresh(target_user)
    return {
        "message": f"User {'activated' if target_user.is_active else 'deactivated'} successfully.",
        "user_id": target_user.id,
        "is_active": target_user.is_active
    }


@router.get("/all-dashboard-data/")
async def admin_list_all_rooms(db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    rooms = db.query(Room).all()
    devices = db.query(Device).all()
    app_user = db.query(User).all()
    return {
        "total_rooms": len(rooms),
        "total_devices": len(devices),
        "total_users": len(app_user)
    }


@router.get("/rooms/", response_model=List[RoomResponse])
async def admin_list_all_rooms(db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    rooms = db.query(Room).all()
    return rooms


@router.get("/users/", response_model=List[UserResponse])
async def admin_list_all_users(db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    users = db.query(User).all()
    return users


@router.get("/devices/", response_model=List[DeviceResponse])
async def admin_list_all_devices(db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    devices = db.query(Device).all()
    return devices

# delete room by admin


@router.delete("/rooms/{room_id}/", status_code=status.HTTP_200_OK)
async def admin_delete_room(room_id: int, db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found."
        )

    db.delete(room)
    db.commit()
    return {"message": "Room deleted successfully."}


@router.delete("/devices/{device_id}/", status_code=status.HTTP_200_OK)
async def admin_delete_device(device_id: int, db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found."
        )

    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully."}


@router.delete("/users/{user_id}/", status_code=status.HTTP_200_OK)
async def admin_delete_user(user_id: int, db: db_dependency, user: admin_dependency):
    # Inline admin verification
    db_user = db.query(Admin).filter(Admin.id == user['user_id']).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    db.delete(target_user)
    db.commit()
    return {"message": "User deleted successfully."}
