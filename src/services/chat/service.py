import asyncio

from fastapi import Depends, WebSocketException
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from src.core.config import settings
from src.core.infrastructure import storage, broker, cluster
from src.core.types import ID
from src.services.chat.dto import INPUT_Message, DTO_Connection
from src.services.chat.repository import DB_GetChat, DB_NewMessage


class SERVICE_SendMessage:
    def __init__(
            self,
            repository: DB_NewMessage = Depends()
    ):
        self.repository = repository

    async def __call__(self, model: INPUT_Message):
        result = await self.repository(model)
        app_id = await storage.get(f"user:{model.recipient_id}")
        await broker.publish(model, stream=f"incoming-message-app-{app_id}")
        return result


class SERVICE_GetChat:
    def __init__(
            self,
            repository: DB_GetChat = Depends()
    ):
        self.repository = repository
        pass

    async def __call__(self, me: ID, him: ID, skip: int, limit: int):
        """Возвращает список последних сообщений отправленных между пользователями"""
        return await self.repository(me, him, skip, limit)


class SERVICE_ReceiveMessage:
    async def listen(self, user_id: ID, ws: WebSocket):
        try:
            while True:
                await ws.receive()
        except (WebSocketDisconnect, RuntimeError):
            await cluster.disconnect(user_id)

    async def __call__(self, user_id: ID, ws: WebSocket):
        old_connection = await storage.get(f"user:{user_id}")
        if old_connection:
            await broker.publish(
                DTO_Connection(
                    user_id=user_id,
                    app_id=settings.APP_GLOBAL_ID
                ),
                stream="kill-old-connection"
            )
        await cluster.save_connection(user_id, ws)
        await ws.accept()
        task = asyncio.create_task(self.listen(user_id, ws))
        await cluster.save_task(user_id, task)
        try:
            await task
        except asyncio.CancelledError:
            print(f"Пользователь {user_id} больше не принимает сообщения в приложении {settings.APP_GLOBAL_ID}")
        finally:
            await cluster.disconnect(user_id)
