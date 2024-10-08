import logging

from fastapi import FastAPI, Depends
from client.mqtt_client import MQTT
from model.constant import Constant
from config.env_config import EnvironmentConfig

class ExtendedFastAPI(FastAPI):
    def __init__(self):
        super().__init__(
            title="MQTT Client API",
            description="API for managing MQTT clients",
            version="1.0.0",
            docs_url="/swagger",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        self.mqtt_client: MQTT = self._initialize_mqtt_client()
        self.logger = self._initialize_logger()
        self._initialize_routers()

    def _initialize_routers(self):
        from router import home_router, auth_router, mqtt_router, client_router
        self.include_router(mqtt_router.router)
        self.include_router(client_router.router)
        self.include_router(auth_router.router)
        self.include_router(home_router.router)

    def _initialize_mqtt_client(self):

        broker = Constant.Broker.HOST
        port = Constant.Broker.PORT
        client_id = Constant.Broker.CLIENT_ID
        username = Constant.Broker.BROKER_USERNAME
        password = Constant.Broker.BROKER_PASSWORD


        mqtt_client = MQTT(broker, port, client_id, username, password)
        mqtt_client.start()
        return mqtt_client

    def _initialize_logger(self):

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        return logger


class AppFactory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppFactory, cls).__new__(cls)
            cls._instance.app_instance = cls._create_app()
            cls._instance.app_instance.logger.info("App instance created")
        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def _create_app():
        return ExtendedFastAPI()

    def get_app(self):
        return self._instance.app_instance
