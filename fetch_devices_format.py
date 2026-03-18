
import json
from sqlalchemy.orm import Session
from app.database import SessionLocale
from app.model.blockchain import UserBlock, DeviceBlock
from app.model.room import Room, Device
from app.model.user import User
from app.schemas.device_schema import DeviceResponse

def show_devices():
    db: Session = SessionLocale()
    try:
        # Fetch 2 devices with their blockchain
        devices = db.query(Device).limit(2).all()
        
        output = []
        for device in devices:
            # Use DeviceResponse to format the data (includes blockchain through relationship)
            # Ensure the relationship is loaded or handle blockchain manually if needed
            device_data = DeviceResponse.from_orm(device).dict()
            output.append(device_data)
            
        print(json.dumps(output, indent=4, default=str))
        
    finally:
        db.close()

if __name__ == "__main__":
    show_devices()
