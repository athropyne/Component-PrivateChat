import asyncio
from uuid import UUID

import redis
from redis.asyncio import Redis
from starlette.websockets import WebSocket

from src.core.config import settings
from src.core.types import APP_ID, ID


class AppCluster:
    def __init__(
            self,
            _storage: Redis
    ):
        self.storage = _storage
        self.instances: set[UUID] = set()
        self.connections: dict[ID, WebSocket] = {}
        self.instance_heartbeat_task: asyncio.Task | None = None
        self.cluster_healthcheck_task: asyncio.Task | None = None
        self.connections_heartbeat_task: asyncio.Task | None = None

    async def instance_heartbeat(self, app_id: APP_ID, app_address: str):
        try:
            while True:
                await self.storage.set(f"app:{app_id}", app_address, ex=10)
                await asyncio.sleep(5)
        except Exception as e:
            print(e)

    async def cluster_healthcheck(self):
        try:
            while True:
                apps = await self.storage.keys(pattern="app:*")
                self.instances = set(apps)
                await asyncio.sleep(5)
        except redis.exceptions.ConnectionError as e:
            print(e)

    async def connections_heartbeat(self):
        try:
            while True:
                try:
                    pipe = self.storage.pipeline()
                    for user_id in self.connections.keys():
                        pipe.set(f"user:{user_id}", str(settings.APP_GLOBAL_ID), ex=10)
                    await pipe.execute()
                except Exception as e:
                    print(f"Error in connections_heartbeat: {e}")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("connections_heartbeat task cancelled")
        except Exception as e:
            print(f"FATAL error in connections_heartbeat: {e}")

    async def start(self, app_address: str):
        self.instance_heartbeat_task = asyncio.create_task(self.instance_heartbeat(settings.APP_GLOBAL_ID, app_address))
        self.cluster_healthcheck_task = asyncio.create_task(self.cluster_healthcheck())
        self.connections_heartbeat_task = asyncio.create_task(self.connections_heartbeat())

    async def stop(self):
        self.instance_heartbeat_task.cancel()
        self.cluster_healthcheck_task.cancel()
        self.connections_heartbeat_task.cancel()
