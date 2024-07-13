from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from factory import AppFactory


router = APIRouter()


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
        raise HTTPException(status_code=500, detail="Error publishing message")

@router.post("/subscribe")
async def subscribe_topic(topic: SubscribeTopic):
    app = AppFactory().get_app()

    try:
        app.mqtt_client.subscribe(topic.topic, topic.qos)
        return {"status": "Subscribed to topic successfully"}
    except Exception as e:
        app.logger.error(f"Error subscribing to topic: {e}")
        raise HTTPException(status_code=500, detail="Error subscribing to topic")

@router.post("/unsubscribe")
async def unsubscribe_topic(topic: UnsubscribeTopic):
    app = AppFactory().get_app()

    try:
        app.mqtt_client.unsubscribe(topic.topic)
        return {"status": "Unsubscribed from topic successfully"}
    except Exception as e:
        app.logger.error(f"Error unsubscribing from topic: {e}")
        raise HTTPException(status_code=500, detail="Error unsubscribing from topic")


