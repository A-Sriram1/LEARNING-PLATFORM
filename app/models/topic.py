import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Topic(Base):
    """One row per learning workspace a user has generated (e.g. 'Java Arrays')."""
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="generating")  # generating | ready | failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TopicContent(Base):
    """Generated content per tab (roadmap, theory, cheat_sheet, ...). One row per tab
    keeps generation independently retryable/cacheable instead of one giant blob."""
    __tablename__ = "topic_contents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("topics.id"), index=True)
    section: Mapped[str] = mapped_column(String)  # roadmap|theory|syntax|cheat_sheet|mistakes|resources|summary
    content: Mapped[dict] = mapped_column(JSON)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
