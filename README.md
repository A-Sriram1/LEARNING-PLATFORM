# SkillForge AI — Backend

FastAPI service. Auth is delegated entirely to **Supabase Auth**; this API
only verifies the JWT Supabase issues (see `app/core/security.py`) — it
never stores passwords or implements its own login flow.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your own values — never commit real secrets
uvicorn app.main:app --reload
```

## Architecture

```
app/
  core/       settings (env-driven) + JWT verification
  db/         async SQLAlchemy engine/session
  models/     ORM tables (see schema below)
  schemas/    Pydantic request/response bodies
  services/   ai_service.py (OpenAI/Gemini prompts) · judge0_service.py (code execution)
  routers/    one router per feature area, thin — logic lives in services/
```

Generation is fanned out as a background task (`topics.py`) so
`POST /topics` returns instantly with `status="generating"`; the frontend
subscribes to the `topics` row via Supabase Realtime (or polls
`GET /topics/{id}`) to know when it flips to `"ready"`.

## Database schema (Postgres via Supabase)

| Table | Purpose |
|---|---|
| `users` | mirrors `auth.users`; XP, coins, level, streak |
| `topics` | one row per generated workspace |
| `topic_contents` | one row per tab (roadmap/theory/cheat_sheet/...), independently generated & cacheable |
| `coding_problems` | AI-generated problems per topic, with visible + hidden test cases |
| `submissions` | run history, pass/fail, exec time, AI code review |
| `mcqs` / `mcq_attempts` | question bank + per-user attempt log |
| `interview_sessions` / `interview_reports` | voice interview transcript + final scored report |
| `achievements` / `user_achievements` / `xp_transactions` | gamification ledger |
| `chat_conversations` / `chat_messages` | AI chat history, supports bookmarking |

All tables use UUID primary keys so IDs are safe to expose in URLs and
generate client-side before a round trip if needed.

## API surface (v1)

```
POST   /topics                       create a workspace from one topic string
GET    /topics/{id}                  poll generation status + read metadata

POST   /coding/run                   run source against custom stdin (no scoring)
POST   /coding/submit                run against all test cases, save, AI-review

GET    /mcqs/{topic_id}?difficulty=  fetch a question set
POST   /mcqs/{id}/attempt            submit an answer, get explanation if wrong

POST   /interviews/start             begin a voice interview on a track
POST   /interviews/{id}/respond      submit transcribed answer, get next question
POST   /interviews/{id}/finish       end session, get scored report

GET    /health                       liveness check
```

Not yet scaffolded, same pattern applies: `projects`, `videos` (YouTube
Data API), `chat`, `progress`, `admin/*`. Ask and I'll add them next.

## Security notes

- Every secret is read from environment variables — nothing is hardcoded.
- Any API key that has ever been pasted into a chat, ticket, or shared
  doc should be treated as compromised and rotated before real use.
- Judge0 executes untrusted student code — it runs in Judge0's own
  sandbox, never inside this API process.
