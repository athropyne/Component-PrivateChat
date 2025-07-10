from abc import abstractmethod

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.infrastructure import database
from src.core.utils import catch


class Event(BaseModel):
    pass


class BaseRepository:
    def __init__(self):
        super().__init__()


class BaseService:
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def __call__(self, *args, **kwargs): ...


class FailedConnectionDBMeta(type):
    def __new__(cls, name, bases, namespace):
        if "__call__" in namespace:
            namespace["__call__"] = catch(namespace["__call__"])
        return super().__new__(cls, name, bases, namespace)


class BaseSQLRepository(BaseRepository, metaclass=FailedConnectionDBMeta):
    def __init__(self):
        super().__init__()
        self.engine: AsyncEngine = database()

    @abstractmethod
    @catch
    async def __call__(self, *args, **kwargs):
        pass
