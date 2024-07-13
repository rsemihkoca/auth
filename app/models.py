from sqlalchemy import Column, String, Boolean, DateTime
from database import Base

class MQTTClient(Base):
    __tablename__ = "mqtt_client"

    serial_number = Column(String, primary_key=True, index=True)
    target = Column(String, default="")
    is_disabled = Column(Boolean, default=False)
    last_update_time = Column(String)
