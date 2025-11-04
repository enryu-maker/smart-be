from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    space_name = Column(String)
    space_type = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="rooms")

    # ✅ Add this missing relationship (fixes your error)
    devices = relationship("Device", back_populates="room",
                           cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False)
    device_name = Column(String)
    device_type = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)

    # Device status (on/off)
    is_on = Column(Boolean, default=False)

    # Foreign key to Room
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    # Relationship back to Room
    room = relationship("Room", back_populates="devices")
