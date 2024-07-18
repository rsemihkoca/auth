import hashlib
from fastapi import APIRouter, Depends

from database.db import get_db, SessionLocal
from database.models import MQTTClient
from factory import AppFactory
from model.dto import BrokerAuthenticationResponse, BrokerAuthenticationRequest
router = APIRouter(
    # prefix="/mqtt",
    tags=["AUTH"],
    responses={404: {"description": "Not found"}},
)


@router.post("/auth", response_model=BrokerAuthenticationResponse)
async def authenticate(request: BrokerAuthenticationRequest,
                       db: SessionLocal = Depends(get_db)):
    clientid = request.client_id
    app = AppFactory().get_app()

    client = db.query(MQTTClient).filter(MQTTClient.client_id == clientid).first()
    if not client:
        app.logger.error(f"Client not found: {clientid}")
        return BrokerAuthenticationResponse(result="deny")

    if client.is_disabled:
        app.logger.error(f"Client is disabled: {clientid}")
        return BrokerAuthenticationResponse(result="deny")

    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()

    if hashed_password != client.hashed_password:
        app.logger.error(f"Invalid password: {clientid}")
        return BrokerAuthenticationResponse(result="deny")

    return BrokerAuthenticationResponse(result="allow", is_superuser=client.is_superuser)
