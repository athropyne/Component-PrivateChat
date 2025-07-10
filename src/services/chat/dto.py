from pydantic import BaseModel

from src.core.types import ID, APP_ID


class INPUT_Message(BaseModel):
    sender_id: ID
    recipient_id: ID
    text: str


class DTO_Connection(BaseModel):
    user_id: ID
    app_id: APP_ID
