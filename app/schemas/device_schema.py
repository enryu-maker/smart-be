from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DeviceBase(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None


class DeviceCreate(DeviceBase):
    room_id: int  # Required when creating a device


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    is_on: Optional[bool] = None


class DeviceResponse(DeviceBase):
    id: int
    is_on: bool
    date_added: datetime
    room_id: int

    class Config:
        from_attributes = True  # For ORM model support
