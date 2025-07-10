from faststream.redis import RedisRouter

from src.core.config import settings
from src.core.infrastructure import cluster
from src.services.chat.dto import DTO_Connection, INPUT_Message

event_router = RedisRouter()


@event_router.subscriber(stream="kill-old-connection")
async def kill_old_connection_handler(
        connection: DTO_Connection,
):
    if connection.app_id != settings.APP_GLOBAL_ID and connection.user_id in cluster.connections:
        del cluster.connections[connection.user_id]


@event_router.subscriber(stream=f"incoming-message-app-{settings.APP_GLOBAL_ID}")
async def handle(
        msg: INPUT_Message,
):
    ws = cluster.connections.get(msg.recipient_id)
    if ws:
        try:
            await ws.send_json(msg.model_dump())
        except Exception as e:
            print(e)
