from functools import wraps
from typing import Callable

import sqlalchemy
from fastapi import HTTPException
from starlette import status


def catch(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except sqlalchemy.exc.OperationalError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail="База данных не отвечает")
        except Exception as e:
            print(e)
            raise

    return wrapper





