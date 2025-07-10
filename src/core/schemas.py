import datetime

from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime, Boolean, false

metadata = MetaData()
messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sender_id", Integer, nullable=False),
    Column("recipient_id", Integer, nullable=False),
    Column("text", String(1000), nullable=False),
    Column("read_it", Boolean, nullable=False, default=false()),
    Column("created_at", DateTime, default=datetime.datetime.now, nullable=False)
)
