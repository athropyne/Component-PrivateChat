from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class Database:
    def __init__(
            self,
            user: str,
            password: str,
            socket: str,
            name: str,
            write_logs: bool = True
    ):
        self._engine = create_async_engine(f"postgresql+asyncpg://{user}:{password}@{socket}/{name}", echo=write_logs)

    async def init(self, metadata: MetaData):
        async with self._engine.connect() as connection:
            # await connection.run_sync(metadata.drop_all)
            await connection.run_sync(metadata.create_all)
            await connection.commit()
        await self._engine.dispose(close=True)

    def __call__(self) -> AsyncEngine:
        return self._engine
