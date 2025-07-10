import asyncio
import pathlib

import fastapi_cli.cli

from src.core.config import settings

if __name__ == '__main__':
    import platform
    if platform.system() == "Windows":
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    fastapi_cli.cli.run(
        pathlib.Path("src/app.py"),
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT
    )
