from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.user import BlockchainBlockResponse


class DeviceBase(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None


class DeviceCreate(DeviceBase):
    room_id: int  # Required when creating a device


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    is_on: Optional[bool] = None
    status_code: Optional[int] = None


class DeviceStatusUpdate(BaseModel):
    device_status: bool
    device_type: str
    status_code: int


class DeviceResponse(DeviceBase):
    id: int
    is_on: bool
    status_code: int
    date_added: datetime
    room_id: int
    blockchain: List[BlockchainBlockResponse] = []

    class Config:
        from_attributes = True  # For ORM model support


class DeviceActionResponse(BaseModel):
    press_id: str
    device_id: int
    device_status: bool
    device_type: str
    status_code: int
    is_pressed: bool
    timestamp: datetime

    class Config:
        from_attributes = True
