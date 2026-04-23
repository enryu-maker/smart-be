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

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="rooms")

    devices = relationship("Device", back_populates="room",
                           cascade="all, delete-orphan")
    blockchain = relationship(
        "DeviceBlock", back_populates="room", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String)
    device_type = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    is_on = Column(Boolean, default=False)
    status_code = Column(Integer, default=0)

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    room = relationship("Room", back_populates="devices")

    blockchain = relationship(
        "DeviceBlock", back_populates="device", cascade="all, delete-orphan")


class DeviceAction(Base):
    __tablename__ = "device_actions"

    id = Column(Integer, primary_key=True, index=True)
    press_id = Column(String, unique=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    device_status = Column(Boolean)
    device_type = Column(String)
    status_code = Column(Integer)
    is_pressed = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    device = relationship("Device")
