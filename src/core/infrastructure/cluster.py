import dataclasses

from pydantic import BaseModel
import asyncio
from uuid import UUID

import redis
from redis.asyncio import Redis
from starlette.websockets import WebSocket, WebSocketState

from src.core.config import settings
from src.core.types import APP_ID, ID


@dataclasses.dataclass
class Connection:
    ws: WebSocket
    task: asyncio.Task | None


class AppCluster:
    def __init__(
            self,
            _storage: Redis,
            ttl: int = 10,
            recovery_second: int = 5
    ):
        assert ttl > recovery_second
        self.storage = _storage
        self.instances: set[UUID] = set()
        self.connections: dict[ID, Connection] = {}
        self.ttl = ttl
        self.recovery_second = recovery_second
        self.instance_heartbeat_task: asyncio.Task | None = None
        self.cluster_healthcheck_task: asyncio.Task | None = None
        self.connections_heartbeat_task: asyncio.Task | None = None

    async def instance_heartbeat(self, app_id: APP_ID, app_address: str):
        try:
            while True:
                await self.storage.set(f"app:{app_id}", app_address, ex=self.ttl)
                await asyncio.sleep(self.recovery_second)
        except Exception as e:
            print(e)

    async def cluster_healthcheck(self):
        try:
            while True:
                apps = await self.storage.keys(pattern="app:*")
                self.instances = set(apps)
                await asyncio.sleep(self.recovery_second)
        except redis.exceptions.ConnectionError as e:
            print(e)

    async def connections_heartbeat(self):
        try:
            while True:
                try:
                    pipe = self.storage.pipeline()
                    for user_id in self.connections.keys():
                        pipe.set(f"user:{user_id}", str(settings.APP_GLOBAL_ID), ex=self.ttl)
                    await pipe.execute()
                except Exception as e:
                    print(f"Error in connections_heartbeat: {e}")
                await asyncio.sleep(self.recovery_second)
        except asyncio.CancelledError as e:
            print(e)
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

    async def save_connection(self, user_id: ID, ws: WebSocket):
        await self.storage.set(f"user:{user_id}", str(settings.APP_GLOBAL_ID), ex=self.ttl)
        self.connections[user_id] = Connection(ws=ws, task=None)

    async def save_task(self, user_id: ID, task: asyncio.Task):
        self.connections[user_id].task = task

    async def disconnect(self, user_id: ID):
        await self.storage.delete(f"user:{user_id}")
        connection = self.connections.pop(user_id, None)
        if connection:
            if connection.ws:
                if connection.ws.client_state != WebSocketState.DISCONNECTED:
                    await connection.ws.close()
            if not connection.task.cancelled():
                connection.task.cancel()
