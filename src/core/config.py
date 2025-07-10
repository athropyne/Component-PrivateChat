import uuid
from uuid import UUID

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_GLOBAL_ID: UUID = uuid.uuid4()
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000

    # redis broker
    REDIS_BROKER_LOGIN: str = "redis"
    REDIS_BROKER_PASSWORD: str = "redis"
    REDIS_BROKER_SOCKET: str = "localhost:6379"
    REDIS_BROKER_DB: int = 1

    # databases
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "Component_Chat"
    POSTGRES_SOCKET: str = "localhost"
    POSTGRES_LOGS: bool = True


settings = Settings()
