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


@router.get("/admin/all-dashboard-data/")
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


@router.get("/admin/rooms/", response_model=List[RoomResponse])
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


@router.get("/admin/users/", response_model=List[UserResponse])
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


@router.get("/admin/devices/", response_model=List[DeviceResponse])
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
