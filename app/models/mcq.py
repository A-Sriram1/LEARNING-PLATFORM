import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class MCQ(Base):
    __tablename__ = "mcqs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("topics.id"), index=True)
    difficulty: Mapped[str] = mapped_column(String)
    question: Mapped[str] = mapped_column(String)
    options: Mapped[dict] = mapped_column(JSON)          # ["A", "B", "C", "D"]
    correct_index: Mapped[int] = mapped_column()
    explanation: Mapped[str] = mapped_column(String)
    why_wrong: Mapped[dict] = mapped_column(JSON)         # {option_index: reason}
    related_topic: Mapped[str | None] = mapped_column(String, nullable=True)


class MCQAttempt(Base):
    __tablename__ = "mcq_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    mcq_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("mcqs.id"), index=True)
    selected_index: Mapped[int] = mapped_column()
    is_correct: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
