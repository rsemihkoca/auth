import os
from dotenv import load_dotenv

class EnvironmentConfig:
    def __init__(self, env_file='./.env'):
        self.env_file = env_file
        self.load_env()

    def load_env(self):
        load_dotenv(self.env_file)

    def get(self, key, default=None):
        return os.getenv(key, default)


