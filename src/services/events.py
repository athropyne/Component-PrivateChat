from faststream.redis import RedisRouter

from src.core.config import settings
from src.core.infrastructure import cluster
from src.services.chat.dto import DTO_Connection, INPUT_Message

event_router = RedisRouter()



