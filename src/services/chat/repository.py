from sqlalchemy import Executable, CursorResult, select
from sqlalchemy.sql.operators import or_, and_

from src.core.interfaces import BaseSQLRepository
from src.core.schemas import messages
from src.core.types import ID
from src.services.chat.dto import INPUT_Message, OUTPUT_Message


class DB_NewMessage(BaseSQLRepository):
    def _stmt(self, model: INPUT_Message) -> Executable:
        return (
            messages
            .insert()
            .values(model.model_dump())
            .returning(messages)
        )

    async def __call__(self, model: INPUT_Message) -> OUTPUT_Message:
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(model))
            await connection.commit()
        return OUTPUT_Message(**cursor.mappings().fetchone())


class DB_GetChat(BaseSQLRepository):
    def _stmt(self, me: ID, him: ID, skip: int, limit: int) -> Executable:
        return (
            select(messages)
            .where(
                or_(
                    and_(
                        messages.c.sender_id == me,
                        messages.c.recipient_id == him
                    ),
                    and_(
                        messages.c.sender_id == him,
                        messages.c.recipient_id == me
                    )
                )
            )
            .order_by(messages.c.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

    async def __call__(self, me: ID, him: ID, skip: int, limit: int) -> list[OUTPUT_Message]:
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self._stmt(me, him, skip, limit))
        result = list(cursor.mappings().fetchall())
        result.reverse()
        return [OUTPUT_Message(**message) for message in result]
