from fastapi import APIRouter
from pydantic import BaseModel, Field
from starlette import status
from starlette.websockets import WebSocket

from src.core.infrastructure import storage
from src.core.types import APP_ID, ID

cluster_router = APIRouter(prefix="/cluster", tags=["cluster"])


class OUTPUT_InstanceInfo(BaseModel):
    app_id: APP_ID = Field(..., description="ID экземпляра")
    is_alive: bool = Field(..., description="Живой или нет")
    connections: dict[ID, WebSocket] = Field(..., description="Локально сохраненные подключения")
    remote_saved_connections: set[ID] = Field(..., description="Подключения видимые в сети кластера")


@cluster_router.get(
    "/instance",
    status_code=status.HTTP_200_OK,
    summary="Получить информацию об этом экземпляре"
)
async def get_instance_info():
    _remote_saved_connections = await storage.scan()
