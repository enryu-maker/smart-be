from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.device_schema import DeviceResponse
from app.schemas.user import BlockchainBlockResponse


class RoomBase(BaseModel):
    space_name: str
    space_type: Optional[str] = None


class RoomCreate(RoomBase):
    user_id: int  # Link room to user


class RoomResponse(RoomBase):
    id: int
    date_added: datetime
    user_id: int
    devices: List[DeviceResponse] = []  # Nested devices
    blockchain: List[BlockchainBlockResponse] = []  # Room's device-related blocks

    class Config:
        from_attributes = True
