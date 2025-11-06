import hashlib
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import datetime


class DeviceBlock(Base):
    __tablename__ = "device_blocks"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(Text)  # JSON string of device info
    previous_hash = Column(String, nullable=True)
    hash = Column(String, nullable=False)

    room = relationship("Room", back_populates="blockchain")

    def calculate_hash(self):
        """Generate SHA256 hash of block contents"""
        block_content = f"{self.room_id}{self.device_id}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_content.encode()).hexdigest()
