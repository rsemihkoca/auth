from pydantic import BaseModel


class ClientCreateRequest(BaseModel):
    client_id: str
    username: str

class BrokerResponse(BaseModel):
    broker: str
    port: int
    client_id: str
    username: str
    password: str

class ClientCreateResponse(BaseModel):
    broker_cred: BrokerResponse
    topics: list[dict[str, str]]
    # publish_topic: str
    # log_topic: str
    # state_topic: str
    # command_topic: str


class BrokerAuthenticationRequest(BaseModel):
    username: str
    password: str


class BrokerAuthenticationResponse(BaseModel):
    result: str = "deny"  #  options: "allow" | "deny" | "ignore"
    is_superuser: bool = False  # options: true | false, default value: false
    class Config:
        # This ensures that any extra fields in the input JSON are ignored
        extra = "ignore"
