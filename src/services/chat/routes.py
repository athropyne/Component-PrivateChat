from fastapi import APIRouter, Depends
from faststream.redis.fastapi import RedisRouter
from starlette import status
from starlette.websockets import WebSocket

from src.core.config import settings
from src.core.infrastructure import cluster
from src.core.types import ID
from src.services.chat.dto import INPUT_Message, DTO_Connection, OUTPUT_Message
from src.services.chat.service import SERVICE_SendMessage, SERVICE_ReceiveMessage, SERVICE_GetChat

# Not working
# connection_url = f"redis://{settings.REDIS_BROKER_LOGIN}:{settings.REDIS_BROKER_PASSWORD}@{settings.REDIS_BROKER_SOCKET}/{settings.REDIS_BROKER_DB}"


chat_router = RedisRouter(
    prefix="/chat"
)


@chat_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Отправить сообщение в чат",
    description="""
    Отправляет сообщение в чат с пользователем
    """,
    response_model=OUTPUT_Message
)
async def send_message(
        model: INPUT_Message,
        service: SERVICE_SendMessage = Depends()
):
    return await service(model)


@chat_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список сообщений с пользователем",
    description="""
    Возвращает список последний сообщений с пользователем отсортированных по дате
    """,
    response_model=list[OUTPUT_Message]
)
async def get_chat(
        user_1: ID,
        user_2: ID,
        skip: int = 0,
        limit: int = 30,
        service: SERVICE_GetChat = Depends()
):
    return await service(user_1, user_2, skip, limit)


@chat_router.websocket(
    "/ws/{user_id}",
    name="Прием сообщений"
)
async def websocket(
        user_id: ID,
        ws: WebSocket,
        service: SERVICE_ReceiveMessage = Depends()
):
    await service(user_id, ws)


@chat_router.subscriber(stream="kill-old-connection")
async def kill_old_connection_handler(
        connection: DTO_Connection,
):
    if connection.app_id != settings.APP_GLOBAL_ID and connection.user_id in cluster.connections:
        await cluster.disconnect(connection.user_id)
    else:
        print("Старое подключение не удалено")


@chat_router.subscriber(stream=f"incoming-message-app-{settings.APP_GLOBAL_ID}")
async def handle(
        msg: INPUT_Message,
):
    ws = cluster.connections.get(msg.recipient_id)
    if ws:
        try:
            await ws.send_json(msg.model_dump())
        except Exception as e:
            print(e)
