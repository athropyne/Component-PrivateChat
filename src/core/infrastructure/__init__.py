from faststream import FastStream
from faststream.redis import RedisBroker
from redis.asyncio import Redis

from src.core.config import settings
from src.core.infrastructure.cluster import AppCluster
from src.core.infrastructure.postgresql import Database

database = Database(
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    socket=settings.POSTGRES_SOCKET,
    name=settings.POSTGRES_DB,
    write_logs=settings.POSTGRES_LOGS
)
storage = Redis(decode_responses=True)
broker = RedisBroker("redis://localhost:6379")
stream = FastStream(broker)
cluster = AppCluster(storage)

