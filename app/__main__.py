import time

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, MQTTClient
from mqtt_client import MQTT
import uvicorn
import datetime
from logging import getLogger
# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MQTT Client API",
    description="API for managing MQTT clients",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the MQTT Client API"}

@app.post("/client", response_model=ClientCreateResponse)
def create_client(request: ClientCreateRequest, db: Session = Depends(get_db)):
    mac_address = request.mac_address
    existing_client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Client already exists")

    new_client = MQTTClient(
        serial_number=mac_address,
        target="",
        is_disabled=False,
        last_update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
def get_client_status(mac_address: str, db: Session = Depends(get_db)):
    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return not client.is_disabled

@app.post("/client/{mac_address}/enable")
def enable_client(mac_address: str, db: Session = Depends(get_db)):
    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_disabled = False
    db.commit()
    return {"detail": "Client enabled"}

@app.post("/client/{mac_address}/disable")
def disable_client(mac_address: str, db: Session = Depends(get_db)):
    client = db.query(MQTTClient).filter(MQTTClient.serial_number == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_disabled = True
    db.commit()
    return {"detail": "Client disabled"}

if __name__ == "__main__":
    logger = getLogger("uvicorn.error")
    broker = "emqx.local"
    port = 1883
    client_id = "auth_client"
    username = "ubuntu"
    password = "Qq\"123456"

    mqtt_client = MQTT(broker, port, client_id, username, password)
    mqtt_client.start()

    logger.log(10, "MQTT client started")
    # try:
    #     mqtt_client.subscribe("initial/topic")
    #     time.sleep(2)
    #     mqtt_client.unsubscribe("initial/topic")
    #     time.sleep(2)
    #     mqtt_client.subscribe("another/topic")
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     mqtt_client.stop()

    uvicorn.run(app, host="0.0.0.0", port=8000)
