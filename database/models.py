from sqlalchemy import Column, String, Boolean, DateTime
from database.db import Base

class MQTTClient(Base):
    __tablename__ = "mqtt_client"

    client_id = Column(String, primary_key=True, index=True)
    username = Column(String, primary_key=True, index=True)
    password = Column(String)
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)
    target = Column(String, default="")
    is_disabled = Column(Boolean, default=False)
    last_update_time = Column(String)
