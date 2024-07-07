from pydantic import BaseModel

class ClientCreateRequest(BaseModel):
    mac_address: str

class ClientCreateResponse(BaseModel):
    publish_topic: str
    log_topic: str
    state_topic: str
    command_topic: str
