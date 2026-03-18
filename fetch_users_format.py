
import json
from sqlalchemy.orm import Session
from app.database import SessionLocale
from app.model.blockchain import UserBlock, DeviceBlock
from app.model.room import Room, Device
from app.model.user import User
from app.schemas.user import UserResponse
from app.schemas.room_schema import RoomResponse

def show_users():
    db: Session = SessionLocale()
    try:
        # Fetch 2 users with their blockchain and rooms
        users = db.query(User).limit(2).all()
        
        output = []
        for user in users:
            # Use UserResponse to format the data (includes blockchain)
            user_data = UserResponse.from_orm(user).dict()
            
            # Also fetch rooms for this user
            rooms = db.query(Room).filter(Room.user_id == user.id).all()
            user_data['rooms'] = [RoomResponse.from_orm(room).dict() for room in rooms]
            
            output.append(user_data)
            
        print(json.dumps(output, indent=4, default=str))
        
    finally:
        db.close()

if __name__ == "__main__":
    show_users()
