import datetime

from pydantic import BaseModel, Field

from src.core.types import ID, APP_ID


class INPUT_Message(BaseModel):
    sender_id: ID = Field(..., description="ID отправителя")
    recipient_id: ID = Field(..., description="ID получателя")
    text: str = Field(..., max_length=1000, description="Текст сообщения")


class OUTPUT_Message(BaseModel):
    id: ID = Field(..., description="ID сообщения")
    sender_id: ID = Field(..., description="ID отправителя")
    recipient_id: ID = Field(..., description="ID получателя")
    text: str = Field(..., max_length=1000, description="Текст сообщения")
    read_it: bool = Field(..., description="Прочитано или нет (пока не работает)")
    created_at: datetime.datetime = Field(..., description="Дата отправки сообщения")


class DTO_Connection(BaseModel):
    user_id: ID
    app_id: APP_ID
