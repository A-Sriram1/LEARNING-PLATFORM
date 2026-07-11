import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.models.interview import InterviewSession, InterviewReport
from app.services import ai_service

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/start")
async def start_interview(track: str, db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    session = InterviewSession(id=uuid.uuid4(), user_id=user.id, track=track, transcript=[])
    db.add(session)
    await db.commit()
    await db.refresh(session)

    first_q = await ai_service.generate_interview_question(track, [])
    session.transcript = [{"role": "assistant", "text": first_q["question"]}]
    await db.commit()
    return {"session_id": session.id, "question": first_q["question"]}


@router.post("/{session_id}/respond")
async def respond(
    session_id: uuid.UUID, answer_text: str,
    db: AsyncSession = Depends(get_db),
):
    """`answer_text` is the transcribed text from the frontend's speech-to-text
    call (Whisper/Deepgram/etc run client-side or via a dedicated /voice/transcribe
    endpoint) -- kept separate so this endpoint stays provider-agnostic."""
    session = await db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(404, "Interview session not found")

    session.transcript = session.transcript + [{"role": "user", "text": answer_text}]
    next_q = await ai_service.generate_interview_question(session.track, session.transcript)
    session.transcript = session.transcript + [{"role": "assistant", "text": next_q["question"]}]
    await db.commit()
    return {"question": next_q["question"]}


@router.post("/{session_id}/finish")
async def finish_interview(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    session = await db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(404, "Interview session not found")

    scores = await ai_service.score_interview(session.track, session.transcript)
    report = InterviewReport(session_id=session_id, **scores)
    session.status = "completed"
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report
