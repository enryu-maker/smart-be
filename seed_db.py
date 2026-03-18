
import json
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocale, Base, engine
from app.model.user import User
from app.model.room import Room, Device
from app.model.blockchain import UserBlock, DeviceBlock

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocale()
    
    try:
        # 1. Create Users
        users_data = [
            {"name": "Kira", "email": "kira@example.com", "phone_number": "1234567890"},
            {"name": "John Doe", "email": "john@example.com", "phone_number": "9876543210"},
            {"name": "Alice Smith", "email": "alice@example.com", "phone_number": "1122334455"},
        ]
        
        for u_data in users_data:
            existing = db.query(User).filter(User.phone_number == u_data["phone_number"]).first()
            if existing:
                print(f"User {u_data['name']} already exists.")
                continue
                
            new_user = User(
                name=u_data["name"],
                email=u_data["email"],
                phone_number=u_data["phone_number"],
                is_active=True # Active for demonstration
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Add to blockchain (UserBlock)
            last_user_block = db.query(UserBlock).order_by(UserBlock.id.desc()).first()
            prev_user_hash = last_user_block.hash if last_user_block else None
            
            user_data_json = json.dumps({
                "user_id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "phone_number": new_user.phone_number,
                "timestamp": str(datetime.utcnow())
            })
            
            # Using the same hashing logic as in user.py route
            user_block_content = f"{new_user.id}{user_data_json}{prev_user_hash or ''}"
            user_hash = hashlib.sha256(user_block_content.encode()).hexdigest()
            
            new_user_block = UserBlock(
                user_id=new_user.id,
                data=user_data_json,
                previous_hash=prev_user_hash,
                hash=user_hash,
                timestamp=datetime.utcnow()
            )
            db.add(new_user_block)
            db.commit()
            
            # 2. Add Rooms and Devices
            rooms_data = [
                {"name": "Living Room", "type": "Hall"},
                {"name": "Bedroom", "type": "Bedroom"}
            ]
            
            for r_data in rooms_data:
                new_room = Room(
                    space_name=r_data["name"],
                    space_type=r_data["type"],
                    user_id=new_user.id,
                    date_added=datetime.utcnow()
                )
                db.add(new_room)
                db.commit()
                db.refresh(new_room)
                
                # Add Devices to Room
                if r_data["name"] == "Living Room":
                    devices = [
                        {"name": "Smart Light", "type": "Light"},
                        {"name": "Ceiling Fan", "type": "Fan"},
                        {"name": "Smart AC", "type": "AC"}
                    ]
                else:
                    devices = [
                        {"name": "Bed Lamp", "type": "Light"},
                        {"name": "Air Purifier", "type": "Device"}
                    ]
                    
                for d_data in devices:
                    new_device = Device(
                        device_name=d_data["name"],
                        device_type=d_data["type"],
                        room_id=new_room.id,
                        date_added=datetime.utcnow(),
                        is_on=False
                    )
                    db.add(new_device)
                    db.commit()
                    db.refresh(new_device)
                    
                    # Add to blockchain (DeviceBlock)
                    last_device_block = db.query(DeviceBlock).filter(DeviceBlock.room_id == new_room.id).order_by(DeviceBlock.id.desc()).first()
                    prev_device_hash = last_device_block.hash if last_device_block else None
                    
                    device_data_json = json.dumps({
                        "device_name": new_device.device_name,
                        "device_type": new_device.device_type,
                        "is_on": new_device.is_on,
                        "timestamp": str(datetime.utcnow())
                    })
                    
                    # Using hashing logic from device_routes.py
                    device_block_content = f"{new_room.id}{new_device.id}{device_data_json}{prev_device_hash or ''}"
                    device_hash = hashlib.sha256(device_block_content.encode()).hexdigest()
                    
                    new_device_block = DeviceBlock(
                        room_id=new_room.id,
                        device_id=new_device.id,
                        data=device_data_json,
                        previous_hash=prev_device_hash,
                        hash=device_hash,
                        timestamp=datetime.utcnow()
                    )
                    db.add(new_device_block)
                    db.commit()

        print("Seeding successful!")
        
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
