import asyncio

from fastapi import Depends, WebSocketException
from starlette.websockets import WebSocket

from src.core.config import settings
from src.core.infrastructure import storage, broker, cluster
from src.core.types import ID
from src.services.chat.dto import INPUT_Message, DTO_Connection


class SERVICE_SendMessage:
    def __init__(
            self,
            # repository: DB_SendMessage = Depends()  # это будет сохранять сообщения чата в базе
    ):
        # self.repository = repository
        pass

    async def __call__(self, model: INPUT_Message):
        app_id = await storage.get(f"user:{model.recipient_id}")
        await broker.publish(model, stream=f"incoming-message-app-{app_id}")


class SERVICE_GetChat:
    def __init__(
            self,
            # repository: DB_GetChat = Depends()  # это будет сохранять сообщения чата в базе
    ):
        # self.repository = repository
        pass

    async def __call__(self, user_1: ID, user_2: ID, limit: int):
        """Возвращает список последних сообщений отправленных между пользователями"""
        pass


class SERVICE_ReceiveMessage:
    async def __call__(self, user_id: ID, ws: WebSocket):
        old_connection = await storage.get(f"user:{user_id}")
        if old_connection:
            await broker.publish(DTO_Connection(user_id=user_id, app_id=settings.APP_GLOBAL_ID),
                                 stream="kill-old-connection")
        await storage.set(f"user:{user_id}", str(settings.APP_GLOBAL_ID), ex=10)
        cluster.connections[user_id] = ws
        await ws.accept()
        try:
            while True:
                if user_id not in cluster.connections:
                    break
                await asyncio.sleep(0)
        except WebSocketException as e:
            await storage.delete(f"user:{user_id}")
            del cluster.connections[user_id]
        await ws.close()
