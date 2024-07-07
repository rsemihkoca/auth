from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, MQTTClient
import mqtt

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request and response
class ClientCreateRequest(BaseModel):
    mac_address: str

class ClientCreateResponse(BaseModel):
    publish_topic: str
    log_topic: str
    state_topic: str
    command_topic: str

@app.post("/client", response_model=ClientCreateResponse)
def create_client(request: ClientCreateRequest, db: Session = next(get_db())):
    mac_address = request.mac_address
    existing_client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Client already exists")

    new_client = MQTTClient(
        serial_number=mac_address,
        target="",
        is_disabled=False,
        last_update_time=None
    )
    db.add(new_client)
    db.commit()

    # Publish MQTT message
    mqtt.publish_message(f"CLIENT/{mac_address}/LOG", "Device record and topic created")

    response = ClientCreateResponse(
        publish_topic=f"CLIENT/{mac_address}/INFERENCE",
        log_topic=f"CLIENT/{mac_address}/LOG",
        state_topic=f"CLIENT/{mac_address}/STATE",
        command_topic=f"CLIENT/{mac_address}/COMMAND"
    )
    return response

@app.get("/client/{mac_address}", response_model=bool)
def get_client_status(mac_address: str, db: Session = next(get_db())):
    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return not client.is_disabled

@app.post("/client/{mac_address}/enable")
def enable_client(mac_address: str, db: Session = next(get_db())):
    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_disabled = False
    db.commit()
    return {"detail": "Client enabled"}

@app.post("/client/{mac_address}/disable")
def disable_client(mac_address: str, db: Session = next(get_db())):
    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_disabled = True
    db.commit()
    return {"detail": "Client disabled"}


