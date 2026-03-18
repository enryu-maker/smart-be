from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BlockchainBlockResponse(BaseModel):
    id: int
    timestamp: datetime
    data: str
    previous_hash: Optional[str]
    hash: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=10)


class OTPVerify(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=10)
    otp: int


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    is_active: bool
    blockchain: List[BlockchainBlockResponse] = []

    class Config:
        from_attributes = True
