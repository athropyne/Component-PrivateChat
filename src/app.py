from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.infrastructure import storage, broker, cluster, database
from src.core.schemas import metadata
from src.services.events import event_router
from src.services.chat.routes import chat_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await cluster.start(f"{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    await broker.start()
    await database.init(metadata)
    yield
    await cluster.stop()
    await storage.delete(f"app:{settings.APP_GLOBAL_ID}")
    await broker.close()


app = FastAPI(lifespan=lifespan)

# broker.include_router(event_router)
app.include_router(chat_router)
