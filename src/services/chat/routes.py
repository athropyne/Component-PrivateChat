from fastapi import APIRouter, Depends
from starlette import status
from starlette.websockets import WebSocket

from src.core.types import ID
from src.services.chat.dto import INPUT_Message
from src.services.chat.service import SERVICE_SendMessage, SERVICE_ReceiveMessage

chat_router = APIRouter(prefix="/chat")


@chat_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Отправить сообщение в чат",
    description="""
    Отправляет сообщение в чат с пользователем
    """
)
async def send_message(
        model: INPUT_Message,
        service: SERVICE_SendMessage = Depends()
):
    await service(model)


@chat_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список сообщений с пользователем",
    description="""
    Возвращает список последний сообщений с пользователем отсортированных по дате
    """
)
async def get_chat(
        user_1: ID,
        user_2: ID,
        limit: int = 30,
        service: SERVICE_GetChat = Depends()
):
    return await service(
        user_1,
        user_2,
        limit
    )


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
