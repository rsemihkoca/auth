
from config.env_config import EnvironmentConfig

env = EnvironmentConfig()


class Constant:

    class Datetime:
        class Format:
            DATE = "%Y-%m-%d"
            TIME = "%H:%M:%S"
            DATETIME = "%Y-%m-%d %H:%M:%S"

    class Broker:
        HOST = env.get('BROKER')
        PORT = env.get('PORT')
        CLIENT_ID = env.get('CLIENT_ID')
        BROKER_USERNAME = env.get('BROKER_USERNAME')
        BROKER_PASSWORD = env.get('BROKER_PASSWORD')
        HASHED_PASSWORD = env.get('HASHED_PASSWORD')

