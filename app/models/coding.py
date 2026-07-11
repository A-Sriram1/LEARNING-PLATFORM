import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class CodingProblem(Base):
    __tablename__ = "coding_problems"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("topics.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)  # easy|medium|hard
    prompt: Mapped[str] = mapped_column(Text)
    starter_code: Mapped[dict] = mapped_column(JSON)          # {"python": "...", "java": "..."}
    visible_test_cases: Mapped[dict] = mapped_column(JSON)    # [{"input":..,"output":..}]
    hidden_test_cases: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    problem_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("coding_problems.id"), index=True)
    language: Mapped[str] = mapped_column(String)
    source_code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String)  # pending|accepted|wrong_answer|error|timeout
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    exec_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_kb: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_review: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {complexity, suggestions[]}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
