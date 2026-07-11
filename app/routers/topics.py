"""The core flow: student types ONE topic -> we generate the full workspace.

Generation is kicked off as a background task so the endpoint returns
instantly with status="generating"; the frontend polls or subscribes to
Supabase Realtime on the topic row to know when each tab is ready.
"""
import re
import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.models.topic import Topic, TopicContent
from app.schemas.topic import TopicCreateRequest, TopicResponse
from app.services import ai_service

router = APIRouter(prefix="/topics", tags=["topics"])


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


@router.post("", response_model=TopicResponse, status_code=201)
async def create_topic(
    body: TopicCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    topic = Topic(id=uuid.uuid4(), user_id=user.id, title=body.title, slug=slugify(body.title))
    db.add(topic)
    await db.commit()
    await db.refresh(topic)

    background_tasks.add_task(_generate_workspace, topic.id, body.title)
    return topic


async def _generate_workspace(topic_id: uuid.UUID, title: str):
    """Fans out generation across tabs. Each section is generated and saved
    independently so a failure in one (e.g. MCQs) doesn't block the rest."""
    from app.db.session import AsyncSessionLocal

    generators = {
        "roadmap": ai_service.generate_roadmap,
        "theory": ai_service.generate_theory,
        "cheat_sheet": ai_service.generate_cheat_sheet,
    }
    async with AsyncSessionLocal() as db:
        topic = await db.get(Topic, topic_id)
        for section, fn in generators.items():
            try:
                content = await fn(title)
                db.add(TopicContent(topic_id=topic_id, section=section, content=content))
            except Exception as exc:
                db.add(TopicContent(topic_id=topic_id, section=section, content={"error": str(exc)}))
        topic.status = "ready"
        await db.commit()


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")
    return topic
