from faststream import FastStream
from faststream.redis import RedisBroker
from redis.asyncio import Redis

from src.core.infrastructure.cluster import AppCluster

storage = Redis(decode_responses=True)
broker = RedisBroker("redis://localhost:6379")
stream = FastStream(broker)
cluster = AppCluster(storage)

