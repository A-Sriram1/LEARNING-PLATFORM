import re
import httpx
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="SkillForge AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from app.routers import topics, coding, mcq, interview
    app.include_router(topics.router)
    app.include_router(coding.router)
    app.include_router(mcq.router)
    app.include_router(interview.router)
except Exception:
    pass


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── YouTube video search ───────────────────────────────────────────────────
@app.get("/demo/videos")
async def demo_videos(topic: str, lang: str = "tamil"):
    import urllib.parse
    query = f"{topic} tutorial {lang}" if lang == "tamil" else f"{topic} tutorial"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}&sp=CAM%253D"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            html = resp.text
        ids      = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        titles   = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"', html)
        channels = re.findall(r'"ownerText":\{"runs":\[\{"text":"([^"]+)"', html)
        seen, videos = set(), []
        for i, vid in enumerate(ids):
            if vid in seen: continue
            seen.add(vid)
            videos.append({
                "videoId": vid,
                "title":   titles[i]   if i < len(titles)   else f"{topic} Tutorial",
                "channel": channels[i] if i < len(channels) else "YouTube",
            })
            if len(videos) >= 5: break
        return JSONResponse({"videos": videos})
    except Exception as e:
        return JSONResponse({"videos": [], "error": str(e)})


# ── Workspace endpoints ────────────────────────────────────────────────────
class ForgeRequest(BaseModel):
    topic: str


@app.post("/demo/forge")
async def demo_forge(body: ForgeRequest):
    topic = body.topic.strip() or "Python"
    return HTMLResponse(content=_build_workspace_html(topic))


@app.get("/workspace")
async def workspace(topic: str = "Python"):
    return HTMLResponse(content=_build_workspace_html(topic.strip() or "Python"))


# ── Login page ─────────────────────────────────────────────────────────────
@app.get("/login")
async def login_page():
    return HTMLResponse(content=_build_login_html())


# ── Landing page ──────────────────────────────────────────────────────────
_root = Path(__file__).parent.parent


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse(str(_root / "index.html"))


# ═══════════════════════════════════════════════════════════════════════════
# HTML BUILDERS  (imported from pages.py)
# ═══════════════════════════════════════════════════════════════════════════
from app.pages import _build_login_html, _build_workspace_html  # noqa: E402
