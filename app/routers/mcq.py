import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.models.mcq import MCQ, MCQAttempt

router = APIRouter(prefix="/mcqs", tags=["mcqs"])


@router.get("/{topic_id}")
async def list_mcqs(topic_id: uuid.UUID, difficulty: str = "medium", db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MCQ).where(MCQ.topic_id == topic_id, MCQ.difficulty == difficulty)
    )
    return result.scalars().all()


@router.post("/{mcq_id}/attempt")
async def attempt_mcq(
    mcq_id: uuid.UUID, selected_index: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    mcq = await db.get(MCQ, mcq_id)
    if not mcq:
        raise HTTPException(404, "MCQ not found")

    is_correct = selected_index == mcq.correct_index
    db.add(MCQAttempt(user_id=user.id, mcq_id=mcq_id, selected_index=selected_index, is_correct=is_correct))
    await db.commit()

    return {
        "is_correct": is_correct,
        "correct_index": mcq.correct_index,
        "explanation": mcq.explanation,
        "why_wrong": mcq.why_wrong if not is_correct else None,
    }
