import hashlib
import secrets
from datetime import datetime
from http.client import HTTPException

from fastapi import APIRouter, Depends

from database.db import SessionLocal, get_db
from database.models import MQTTClient
from exception.exception import ClientExistException, ClientNotExistException
from factory import AppFactory
from model.constant import Constant
from model.dto import ClientCreateResponse, ClientCreateRequest, BrokerResponse

router = APIRouter(
    tags=["CLIENT"]
)




@router.post("/client", response_model=ClientCreateResponse)
def create_client(request: ClientCreateRequest, db: SessionLocal = Depends(get_db)):
    app = AppFactory().get_app()
    client_id = request.client_id
    username = request.username

    # check if client already exists
    existing_client = db.query(MQTTClient).filter(MQTTClient.client_id == client_id).first()
    if existing_client:
        # raise ClientExistExceptio
        # Publish MQTT message
        app.mqtt_client.publish(f"CLIENT/{existing_client.client_id}/LOG", "Device reconnected to authentication server")
        broker = BrokerResponse(
            broker=Constant.Broker.HOST,
            port=Constant.Broker.PORT,
            client_id=existing_client.client_id,
            username=existing_client.username,
            password=existing_client.password
        )
        topics = [
            # {f"CLIENT/{existing_client.client_id}/KGH": "PUBLISH"},
            {f"CLIENT/{existing_client.client_id}/INFERENCE": "PUBLISH"},
            {f"CLIENT/{existing_client.client_id}/LOG": "PUBLISH"},
            {f"CLIENT/{existing_client.client_id}/STATE": "PUBLISH"},
            {f"CLIENT/{existing_client.client_id}/COMMAND": "SUBSCRIBE"}
        ]
        response = ClientCreateResponse(
            broker_cred=broker,
            topics=topics,
        )
        return response

    # create 8 letter password and hash it
    password = secrets.token_urlsafe(8)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    broker = BrokerResponse(
        broker=Constant.Broker.HOST,
        port=Constant.Broker.PORT,
        client_id=client_id,
        username=username,
        password=password
    )
    new_client = MQTTClient(
        client_id=client_id,
        username=username,
        password=password,
        hashed_password=hashed_password,
        target="",
        is_disabled=False,
        last_update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(new_client)
    db.commit()

    # Publish MQTT message
    app.mqtt_client.publish(f"CLIENT/{client_id}/LOG", "Device record and topic created")

    topics = [
        # {f"CLIENT/{client_id}/KGH": "PUBLISH"},
        {f"CLIENT/{client_id}/INFERENCE": "PUBLISH"},
        {f"CLIENT/{client_id}/LOG": "PUBLISH"},
        {f"CLIENT/{client_id}/STATE": "PUBLISH"},
        {f"CLIENT/{client_id}/COMMAND": "SUBSCRIBE"}
    ]
    response = ClientCreateResponse(
        broker_cred=broker,
        topics=topics,
    )
    return response

@router.post("/client/{client_id}/enable")
def enable_client(client_id: str, db: SessionLocal = Depends(get_db)):

    client = db.query(MQTTClient).filter(MQTTClient.client_id == client_id).first()
    if not client:
        raise ClientNotExistException
    client.is_disabled = False
    db.commit()
    return {"detail": "Client enabled"}


@router.post("/client/{client_id}/disable")
def disable_client(client_id: str, db: SessionLocal = Depends(get_db)):
    client = db.query(MQTTClient).filter(MQTTClient.client_id == client_id).first()
    if not client:
        raise ClientNotExistException
    client.is_disabled = True
    db.commit()
    return {"detail": "Client disabled"}

