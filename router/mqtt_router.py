from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from exception.exception import MQTTException
from factory import AppFactory


router = APIRouter(
    prefix="/mqtt",
    tags=["MQTT"],
    responses={404: {"description": "Not found"}},
)


# Define Pydantic models for request bodies
class PublishMessage(BaseModel):
    topic: str
    payload: str
    qos: Optional[int] = 0
    retain: Optional[bool] = False

class SubscribeTopic(BaseModel):
    topic: str
    qos: Optional[int] = 0

class UnsubscribeTopic(BaseModel):
    topic: str


@router.post("/publish")
async def publish_message(message: PublishMessage):
    app = AppFactory().get_app()

    try:
        app.mqtt_client.publish(message.topic, message.payload, message.qos, message.retain)
        return {"status": "Message published successfully"}
    except Exception as e:
        app.logger.error(f"Error publishing message: {e}")
        raise MQTTException(status_code=500, message="PUBLISH_FAILED", detail=f"Error publishing message: {e}")

@router.post("/subscribe")
async def subscribe_topic(topic: SubscribeTopic):
    app = AppFactory().get_app()

    try:
        app.mqtt_client.subscribe(topic.topic, topic.qos)
        return {"status": "Subscribed to topic successfully"}
    except Exception as e:
        app.logger.error(f"Error subscribing to topic: {e}")
        raise MQTTException(status_code=500, message="SUBSCRIBE_FAILED", detail=f"Error subscribing to topic: {e}")

@router.post("/unsubscribe")
async def unsubscribe_topic(topic: UnsubscribeTopic):
    app = AppFactory().get_app()

    try:
        app.mqtt_client.unsubscribe(topic.topic)
        return {"status": "Unsubscribed from topic successfully"}
    except Exception as e:
        app.logger.error(f"Error unsubscribing from topic: {e}")
        raise MQTTException(status_code=500, message="UNSUBSCRIBE_FAILED", detail=f"Error unsubscribing from topic: {e}")

@router.get("/start")
async def start_mqtt_router(background_tasks: BackgroundTasks):
    app = AppFactory().get_app()
    background_tasks.add_task(app.mqtt_client.start)
    app.logger.info("MQTT router started")
    return {"status": "MQTT router started"}

@router.get("/stop")
async def stop_mqtt_router(background_tasks: BackgroundTasks):
    app = AppFactory().get_app()
    background_tasks.add_task(app.mqtt_client.stop)
    return {"status": "MQTT router stopped"}
