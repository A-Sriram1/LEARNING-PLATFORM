import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.models.coding import CodingProblem, Submission
from app.schemas.coding import RunRequest, SubmitRequest
from app.services import judge0_service, ai_service

router = APIRouter(prefix="/coding", tags=["coding"])


@router.post("/run")
async def run_code(body: RunRequest):
    """Runs against the student's custom input only -- no scoring, no DB write."""
    result = await judge0_service.execute(body.source_code, body.language, body.stdin)
    return result


@router.post("/submit")
async def submit_code(
    body: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    problem = await db.get(CodingProblem, body.problem_id)
    if not problem:
        raise HTTPException(404, "Problem not found")

    all_cases = problem.visible_test_cases + problem.hidden_test_cases
    passed = 0
    max_time = 0.0
    for case in all_cases:
        result = await judge0_service.execute(body.source_code, body.language, case["input"])
        if result["stdout"].strip() == case["output"].strip():
            passed += 1
        max_time = max(max_time, result.get("time_ms") or 0)

    status = "accepted" if passed == len(all_cases) else "wrong_answer"
    ai_review = await ai_service.review_submission(body.source_code, body.language, problem.prompt)

    submission = Submission(
        user_id=user.id, problem_id=problem.id, language=body.language,
        source_code=body.source_code, status=status,
        passed_cases=passed, total_cases=len(all_cases),
        exec_time_ms=max_time, ai_review=ai_review,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission
